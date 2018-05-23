import asyncio
from core.supermodel import Supermodel

class Model(Supermodel):
    """
        sets a number as output that gets incremented each round
    """

    def __init__(self, uuid, name :str):
        super(Model,self).__init__(uuid,name,["num"])
        self.number = -1

    async def func_prep(self):
        self.number = self.number + 1

    async def func_peri(self, prep_to_peri=None):
        self.set_output("num",self.number)