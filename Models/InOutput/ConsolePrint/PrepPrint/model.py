import asyncio
from pyjamas_core.util import Input, Output, Property
from pyjamas_core.supermodel import Supermodel

class Model(Supermodel):
    """
        prints the given input during prep
    """

    def __init__(self, uuid, name :str):
        super(Model, self).__init__(uuid,name)

        self.inputs['to_print'] = Input('To Print', unit='String')

    async def func_prep(self):

        txt = await self.get_input("to_print")
        print(str(txt))