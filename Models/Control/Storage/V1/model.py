import asyncio
from pyjama.core.supermodel import Supermodel

class Model(Supermodel):
    """
        takes a number as input and returns it as output the following round
    """

    def __init__(self, uuid, name: str):
        super(Model, self).__init__(uuid, name,["stored"])
        self.stored = 0
    
    async def func_peri(self, prep_to_peri=None):
        self.set_output("stored",self.stored)

        self.stored = await self.get_input("to_store")