import asyncio
from pyjama.core.supermodel import Supermodel

class Model(Supermodel):
    """
        sets the sum of all inputs as output
    """

    def __init__(self, uuid, name :str):
        super(Model, self).__init__(uuid,name,["sum"])
    
    async def func_peri(self, prep_to_peri=None):
        all_inputs = [await self.get_input(name) for name in self.inputs]
        
        res = sum([i for i in all_inputs])

        self.set_output("sum",res)