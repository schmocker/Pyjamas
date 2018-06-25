import asyncio
import logging
import collections
from core.util import Input, Output, Property
import os
from pathlib import Path
from flask import Markup
from markdown2 import markdown


class Supermodel:
    """Parent class for every model.
    Provides the necessary steps to run and connect the model with others in a simulation.

    Arguments:
        uuid {'Any'} -- the id of the model
        name {str} -- the name of the model
    """


    def __init__(self, uuid, name :str):
        self.id = uuid
        self.name = name
        self.agent = None
        self.inputs = {}
        self.outputs = {}
        self.properties = {}
        self.change_properties = {}
        self.alive = True
        self.model_run = 0

#region logging

    def log_debug(self, msg: str):
        try:
            self.agent.logger.debug(f"[{self.id}][{__name__}][{self.name}] : {msg}")
        except AttributeError:
            pass

    def log_warning(self, msg: str):
        try:
            self.agent.logger.warning(f"[{self.id}][{__name__}][{self.name}] : {msg}")
        except AttributeError:
            pass

    def log_error(self, msg: str):
        try:
            self.agent.logger.error(f"[{self.id}][{__name__}][{self.name}] : {msg}")
        except AttributeError:
            pass

#endregion logging

#region ports

    def link_input(self, output_model: 'Supermodel', output_name: str, input_name: str) -> bool:
        """Connect an input of this model to an output of another model
        
        Arguments:
            output_model {Supermodel} -- the model instance that provides the output
            output_name {str} -- the name of the output port
            input_name {str} -- the name of the input port
        
        Returns:
            {bool} -- True if the inputs could be successfully connected, false otherwise
        """

        try:
            self.inputs[input_name].add_link(output_model,output_name)
            return True
        except KeyError:
            return False

    def unlink_input(self, input_name: str) -> bool:
        """Remove a existing connection
        
        Arguments:
            input_name {str} -- the name of the input
        
        Returns:
            {bool} -- True if the connection could be removed successfully, false otherwise
        """

        try:
            self.inputs[input_name].remove_link()
            return True
        except KeyError:
            return False

    async def get_input(self, input_name: str) -> 'Any':
        """Awaits the connected output
        
        Arguments:
            input_name {str} -- the name of the input
        
        Returns:
            {'Any'} -- the awaited output value
        """

        try:
            return await self.inputs[input_name].get_input()
        except KeyError:
            self.log_error(f'input {input_name} could not retrieve Future')
            self.log_error(f'stopping simulation')
            for task in asyncio.Task.all_tasks():
                task.cancel()

    def set_output(self, output_name: str, output: 'Any'):
        """Set the value of an output
        
        Arguments:
            output_name {str} -- the name of the output
            output {'Any'} -- the value that is to be set
        """

        try:
            self.outputs[output_name].set_output(output)    
            self.log_debug(f"set value for output {output_name}")
        except KeyError:
            self.log_warning(f'could not set output for output_name {output_name}')

    def get_output(self, output_name: str) -> Output:
        return self.outputs[output_name]

    def clean_outputs(self):
        """Removes any set output value from all outputs
        """

        for key in self.outputs:
            self.outputs[key].clean_output()
        self.log_debug("outputs cleaned")

    def get_property(self, property_name: str) -> 'Any':
        try:
            return self.properties[property_name].get_property()
        except KeyError:
            self.log_error(f'could not retrieve property {property_name}')
            return None

    def set_property(self, property_name: str, property_value: 'Any'):
        """Set a value for a property that will be used instantly
        
        Arguments:
            property_name {str} -- the name of the property
            property_value {'Any'} -- the value of the property
        """

        try:
            self.properties[property_name].set_property(property_value)
            self.log_debug(f"set value for property {property_name}")
        except KeyError:
            self.log_warning(f'could not change property for property_name {property_name} : property_name not found')
        except ValueError:
            self.log_warning(f'could not change property for property_name {property_name} : property_type does not fit')

    def set_amend_property(self, property_name: str, property_value: 'Any'):
        """Set a value for a property that will be used starting with the next run
        
        Arguments:
            property_name {str} -- the name of the property
            property_value {'Any'} -- the value of the property
        """

        try:
            self.properties[property_name].set_amend_property(property_value)
            self.log_debug(f"set value for property {property_name}")
        except KeyError:
            self.log_warning(f'could not change property for property_name {property_name}')

    async def _amend(self):
        """Replace the values of the current properties with the amended values
        """

        keys = []
        for key in self.properties:
            try:
                if self.properties[key].amend():
                    keys.append(key)
                    self.log_debug(f'changed property {key}')
            except ValueError:
                self.log_warning(f'could not amend property for property_name {key} : property_type does not fit')
        if keys:
            await self.func_amend(keys)
        self.log_debug("finished amend")

    def get_info(self) -> dict:
        """Returns a dictionary with all the information of all inputs, outputs, properties
        
        Returns:
            dict -- the dictionary carrying the information
        """

        info = {}
        info['id'] = self.id
        info['name'] = self.name
        info['inputs'] = {key: inp.get_port_info() for key,inp in self.inputs.items()}
        info['outputs'] = {key: out.get_port_info() for key,out in self.outputs.items()}
        info['properties'] = {key: prop.get_port_info() for key,prop in self.properties.items()}
        return info

#endregion ports

#region simulation loop

    async def simulation_loop(self):
        """The main simulation loop

        runs the functions prep -> peri -> post -> sync in a loop as long as alive is True
        after exiting the loop the function death is executed once
        """

        self.log_debug("starting simulation loop")
        self.model_run = 0

        while self.alive:

            # start a prep - peri - post loop
            await self._internal_post()

            # wait for all models to finish the loop
            await self._sync()

            # increment model run value
            self.model_run += 1

        self.log_debug("starting func_death")
        await self.func_death()
        self.log_debug("internal loop ended")

    async def _internal_birth(self):

        self.clean_outputs()

        self.log_debug("starting func_birth")
        await self.func_birth()

    async def _internal_prep(self):

        self.log_debug("waiting at prep gate")
        await self.agent.prep_gate.wait()

        # properties are amended before prep to ensure that changes made between post and the opening of the prep gate are applied right away
        await self._amend()

        self.log_debug("starting func_prep")
        return await self.func_prep()

    async def _internal_peri(self):

        prep_result = await self._internal_prep()

        self.log_debug("waiting at peri gate")
        await self.agent.peri_gate.wait()

        self.log_debug("starting func_peri")
        return await self.func_peri(prep_to_peri=prep_result)

    async def _internal_post(self):

        peri_result = await self._internal_peri()

        if self.outputs:
            self.log_debug("sending result data to controller")
            await self.send_result_data()

        self.log_debug("waiting at post gate")
        await self.agent.post_gate.wait()

        self.log_debug("starting func_post")
        return await self.func_post(peri_to_post=peri_result)

    async def _sync(self):
        """Awaits that all models have completed the current prep -> peri -> post run before starting the next run

        Two gates (asyncio.Event) are used to prevent that one model runs through multiple runs without performing a context switch.
        This ensures that all models are always in the same run and it enables to perform actions in between runs
        """

        self.log_debug("waiting at first sync gate")
        await self.agent.syncFirst()
        await self.agent.sync_gate_first.wait()

        await self.func_in_sync()
        self.clean_outputs()
        
        self.log_debug("waiting at second sync gate")
        await self.agent.syncSecond()
        await self.agent.sync_gate_second.wait()

    async def send_result_data(self):
        """Send the values of all outputs to the controller
        """

        data = []
        data.append(self.model_run)

        for key, output in self.outputs.items():
            try:
                res = await output.get_output()
            except Exception:
                self.log_warning(f"could not retrieve result from output {key}")
                res = None

            data_point = (key,res)
            data.append(data_point)
        
        self.agent.send_data_order(self.id, data)

#endregion simulation loop

#region abstract methods

    async def func_birth(self):
        pass
    async def func_prep(self):
        pass
    async def func_peri(self, prep_to_peri=None):
        pass
    async def func_post(self, peri_to_post=None):
        pass
    async def func_in_sync(self):
        pass
    async def func_death(self):
        pass
    async def func_amend(self, keys=[]):
        pass

#endregion abstract methods

#region test model

    @classmethod
    def test(cls, inputs: dict, properties: dict) -> dict:
        """Executes one run of the model with the given inputs and properties
        
        Arguments:
            inputs {dict} -- the inputs to use
            properties {dict} -- the properties to use
        
        Returns:
            dict -- the resulting outputs of the run
        """

        class MockAgent():

            def __init__(self, model):
                self.model = model
                self.model.agent = self
                self.result = None

            def run(self):
                self.loop = asyncio.get_event_loop()

                # sync gates
                self.sync_gate_first = asyncio.Event()
                self.sync_gate_second = asyncio.Event()

                # func gates
                self.prep_gate = asyncio.Event()
                self.peri_gate = asyncio.Event()
                self.post_gate = asyncio.Event()

                # open func gates
                self.prep_gate.set()
                self.peri_gate.set()
                self.post_gate.set()

                birth = asyncio.ensure_future(self.model._internal_birth())
                self.loop.run_until_complete(asyncio.gather(birth))

                prep = asyncio.ensure_future(self.model.simulation_loop())
                self.loop.run_until_complete(asyncio.gather(prep))

                return self.data

            async def syncFirst(self):
                self.model.alive = False
                self.sync_gate_first.set()

            async def syncSecond(self):
                self.model.alive = False
                self.sync_gate_second.set()

            def send_data_order(self, model_id, data):
                self.data = data

        class MockModel(Supermodel):
            def __init__(self):
                super(MockModel, self).__init__(0, "mock")
                for key, value in inputs.items():
                    self.outputs[key] = Output({'name': f'mock input {key}'})
                    self.outputs[key].clean_output()
                    self.outputs[key].set_output(value)

        mock_input_mod = MockModel()
        test_mod = cls(0, "test_model")

        for key in inputs:
            test_mod.link_input(mock_input_mod, key, key)

        for key, value in properties:
            test_mod.set_property(key, value)

        mock_agent = MockAgent(test_mod)

        return mock_agent.run()

#endregion test model