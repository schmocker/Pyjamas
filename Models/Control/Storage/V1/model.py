import asyncio
from core.util import Input, Output, Property
from core.supermodel import Supermodel

class Model(Supermodel):
    """
        takes a number as input and returns it as output the following round
    """

    def __init__(self, uuid, name: str):
        super(Model, self).__init__(uuid, name)

        self.inputs['to_store'] = Input({'name': 'To Store', 'unit': 'num', 'dimensions': []})
        self.outputs['stored'] = Output({'name': 'Stored', 'unit': 'num', 'dimensions': []})

        self.stored = 0
    
    async def func_peri(self, prep_to_peri=None):

        self.set_output("stored",self.stored)

        self.stored = await self.get_input("to_store")