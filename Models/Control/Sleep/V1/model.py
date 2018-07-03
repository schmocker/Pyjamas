import asyncio
from core.util import Input, Output, Property
from core.supermodel import Supermodel

class Model(Supermodel):
    """
        sleeps for a set amount of seconds after receiving the input
        afterwards the inputs gets set as output
    """

    def __init__(self, uuid, name: str):
        super(Model, self).__init__(uuid,name)

        self.inputs['input'] = Input(name='Input')

        self.outputs['output'] = Output(name='Output')

        self.properties['sleep_amount'] = Property(1, float, name='Sleep Amount', unit='s')

    async def func_peri(self, prep_to_peri=None):
        inp = await self.get_input("input")

        sleep_amount = self.get_property('sleep_amount')

        await asyncio.sleep(sleep_amount)

        self.set_output("output", inp)