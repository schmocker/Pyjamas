import asyncio
from pyjama.core.supermodel import Supermodel

class Model(Supermodel):
    """
        prints the given input
    """

    def __init__(self, uuid, name :str):
        super(Model, self).__init__(uuid,name,[])

    async def func_peri(self, prep_to_peri=None):

        txt = await self.get_input("to_print")
        print(txt)