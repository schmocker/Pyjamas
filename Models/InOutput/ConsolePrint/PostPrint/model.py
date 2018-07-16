import asyncio
from core.util import Input, Output, Property
from core.supermodel import Supermodel

class Model(Supermodel):
    """
        prints the given input during post
    """

    def __init__(self, uuid, name :str):
        super(Model, self).__init__(uuid,name)

        self.inputs['to_print'] = Input('To Print', unit='String')

    async def func_post(self, peri_to_post=None):

        txt = await self.get_input("to_print")
        print(str(txt))