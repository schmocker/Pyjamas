import asyncio
from core.supermodel import Supermodel

class Model(Supermodel):
    """
        sleeps for a set amount of seconds during peri
        afterwards the inputs gets set as output
    """

    def __init__(self, uuid, name: str):
        super(Model, self).__init__(uuid,name,["output"])
        self.properties["sleep_amount"] = 1
    
    async def func_peri(self, prep_to_peri=None):
        inp = await self.get_input("input")

        await asyncio.sleep(self.properties["sleep_amount"])

        self.set_output("output", inp)