import asyncio
from pyjamas_core.util import Input, Output, Property
from pyjamas_core.supermodel import Supermodel

class Model(Supermodel):
    """
        takes something as input and returns it as output the following run
    """

    def __init__(self, uuid, name: str):
        super(Model, self).__init__(uuid, name)

        self.inputs['to_store'] = Input('To Store')
        self.outputs['stored'] = Output('Stored')

        self.stored = 0
    
    async def func_peri(self, prep_to_peri=None):

        self.set_output('stored',self.stored)

        self.stored = await self.get_input('to_store')