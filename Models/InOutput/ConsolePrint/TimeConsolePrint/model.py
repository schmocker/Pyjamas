import asyncio
from pyjamas_core.util import Input, Output, Property
from pyjamas_core.supermodel import Supermodel
from time import gmtime, strftime

class Model(Supermodel):
    """
        prints the given input
    """

    def __init__(self, uuid, name :str):
        super(Model, self).__init__(uuid,name)

        self.inputs['time'] = Input({'name': 'time', 'unit': 'float', 'dimensions': []})

    async def func_peri(self, prep_to_peri=None):

        time = await self.get_input("time")


        if type(time) is list:
            t_str = [strftime('%Y-%m-%d %H:%M:%S', gmtime(t)) for t in time]
            print(t_str)

        elif type(time) is float:
            t_str = strftime('%Y-%m-%d %H:%M:%S', gmtime(time))
            print(t_str)

        else:
            print(f"No valid time or time list: {time}")

