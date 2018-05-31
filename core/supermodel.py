import asyncio
import logging

class Supermodel:

    def __init__(self, uuid, name :str, output_names :list):
        self.id = uuid
        self.name = name
        self.agent = None
        self.inputs = {}
        self.output_names = output_names
        self.outputs = {}
        self.properties = {}
        self.change_properties = {}
        self.alive = True

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

    def clean_outputs(self):
        for name in self.output_names:
            self.outputs[name] = asyncio.Future()
        self.log_debug("outputs cleaned")

    def link_input(self, output_model, output_name: str, input_name: str):
        try:
            self.inputs[input_name] = (output_model,output_name)
            return True
        except KeyError:
            return False

    def unlink_input(self, input_name: str):
        try:
            del self.inputs[input_name]
            return True
        except KeyError:
            return False

    def get_input(self, input_name: str):
        try:
            return self.inputs[input_name][0].outputs[self.inputs[input_name][1]]
        except KeyError:
            self.log_warning(f'input {input_name} could not retrieve Future')
            return None

    def set_output(self, output_name: str, output):
        try:
            self.outputs[output_name].set_result(output)      
            self.log_debug(f"set value for output {output_name}")
        except KeyError:
            self.log_warning(f'could not set output for output_name {output_name}')

    def set_property(self, property_name: str, property_value):
        try:
            self.change_properties[property_name] = property_value
            self.log_debug(f"set value for property {property_name}")
        except KeyError:
            self.log_warning(f'could not change property for property_name {property_name}')

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

        # wait for post_gate
        self.log_debug("waiting at post gate")
        await self.agent.post_gate.wait()

        # execute func_post
        self.log_debug("starting func_post")
        return await self.func_post(peri_to_post=peri_result)

    async def _amend(self):

        # apply property changes
        for prop_name, prop_value in self.change_properties.items():
            self.properties[prop_name] = prop_value

        # clear change list
        self.change_properties.clear()
        self.log_debug("finished amend")


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