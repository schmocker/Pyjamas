import asyncio
from pyjama.core.supermodel import Supermodel

class Model(Supermodel):
    """
        sets a constant number as output
    """

    def __init__(self, uuid, name :str):
        super(Model,self).__init__(uuid,name,["const"])
        self.properties["number"] = 0


    async def func_peri(self, prep_to_peri=None):
        self.set_output("const",self.properties["number"])