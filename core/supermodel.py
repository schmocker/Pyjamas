import asyncio
import logging
import collections
from core.util import Input, Output, Property
import os
from pathlib import Path
from flask import Markup
from markdown2 import markdown


class Supermodel:

    def __init__(self, uuid, name :str):
        self.id = uuid
        self.name = name
        self.agent = None
        self.inputs = {}
        self.outputs = {}
        self.properties = {}
        self.change_properties = {}
        self.alive = True

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

#region input

    def link_input(self, output_model, output_name: str, input_name: str):
        try:
            self.inputs[input_name].add_link(output_model,output_name)
            return True
        except KeyError:
            return False

    def unlink_input(self, input_name: str):
        try:
            self.inputs[input_name].remove_link()
            return True
        except KeyError:
            return False

    async def get_input(self, input_name: str):
        try:
            return await self.inputs[input_name].get_input()
        except KeyError:
            self.log_error(f'input {input_name} could not retrieve Future')
            self.log_error(f'stopping simulation')
            for task in asyncio.Task.all_tasks():
                task.cancel()

#endregion input

#region output

    def set_output(self, output_name: str, output):
        try:
            self.outputs[output_name].set_output(output)    
            self.log_debug(f"set value for output {output_name}")
        except KeyError:
            self.log_warning(f'could not set output for output_name {output_name}')

    def get_output(self, output_name: str):
        return self.outputs[output_name]

    def clean_outputs(self):
        for key in self.outputs:
            self.outputs[key].clean_output()
        self.log_debug("outputs cleaned")

#endregion output

#region property

    def get_property(self, property_name):
        try:
            return self.properties[property_name].get_property()
        except KeyError:
            self.log_error(f'could not retrieve property {property_name}')
            return None

    def set_property(self, property_name: str, property_value):
        try:
            self.properties[property_name].set_property(property_value)
            self.log_debug(f"set value for property {property_name}")
        except KeyError:
            self.log_warning(f'could not change property for property_name {property_name} : property_name not found')
        except ValueError:
            self.log_warning(f'could not change property for property_name {property_name} : property_type does not fit')

    def set_amend_property(self, property_name: str, property_value):
        try:
            self.properties[property_name].set_amend_property(property_value)
            self.log_debug(f"set value for property {property_name}")
        except KeyError:
            self.log_warning(f'could not change property for property_name {property_name}')

    async def _amend(self):
        for key in self.properties:
            try:
                self.properties[key].amend()
            except ValueError:
                self.log_warning(f'could not amend property for property_name {key} : property_type does not fit')

        self.log_debug("finished amend")

#endregion property

    def get_info(self):
        info = {}
        info['id'] = self.id
        info['name'] = self.name
        info['inputs'] = {key: inp.get_port_info() for key,inp in self.inputs.items()}
        info['outputs'] = {key: out.get_port_info() for key,out in self.outputs.items()}
        info['properties'] = {key: prop.get_port_info() for key,prop in self.properties.items()}
        return info

#region simulation loop

    async def sync(self):
        self.log_debug("waiting at first sync gate")
        await self.agent.syncFirst()
        await self.agent.sync_gate_first.wait()

        await self.func_in_sync()
        self.clean_outputs()
        
        self.log_debug("waiting at second sync gate")
        await self.agent.syncSecond()
        await self.agent.sync_gate_second.wait()

    async def internal_loop(self):
        self.log_debug("starting internal loop")

        while self.alive:

            # start a prep - peri - post loop
            await self._internal_post()

            # wait for all models to finish the loop
            await self.sync()

        self.log_debug("starting func_death")
        await self.func_death()

        self.log_debug("internal loop ended")

    async def _internal_birth(self):

        self.clean_outputs()

        self.log_debug("starting func_birth")
        await self.func_birth()

    async def _internal_prep(self):

        # wait for prep_gate
        self.log_debug("waiting at prep gate")
        await self.agent.prep_gate.wait()

        # load new properties
        await self._amend()

        # execute func_prep
        self.log_debug("starting func_prep")
        return await self.func_prep()

    async def _internal_peri(self):

        # await prep
        prep_result = await self._internal_prep()

        # wait for peri_gate
        self.log_debug("waiting at peri gate")
        await self.agent.peri_gate.wait()

        # execute func_peri
        self.log_debug("starting func_peri")
        return await self.func_peri(prep_to_peri=prep_result)

    async def _internal_post(self):

        # await peri
        peri_result = await self._internal_peri()

        # send result data to controller
        if self.outputs:
            self.log_debug("sending result data to controller")
            await self.send_result_data()

        # wait for post_gate
        self.log_debug("waiting at post gate")
        await self.agent.post_gate.wait()

        # execute func_post
        self.log_debug("starting func_post")
        return await self.func_post(peri_to_post=peri_result)

    async def send_result_data(self):
        data = []

        for key, output in self.outputs.items():
            try:
                name = output.get_port_info()['name']
            except KeyError:
                name = key

            try:
                res = await output.get_output()
            except Exception:
                self.log_warning(f"could not retrieve result from output {key}")
                res = None

            data_point = (name,res)
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

#endregion abstract methods

