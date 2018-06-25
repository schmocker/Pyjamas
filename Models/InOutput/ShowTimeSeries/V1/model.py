import asyncio
from core.util import Input, Output, Property
from core.supermodel import Supermodel

class Model(Supermodel):
    """
        prints the given input
    """

    def __init__(self, uuid, name :str):
        super(Model, self).__init__(uuid,name)

        self.inputs['times'] = Input({'name': 'Times', 'unit': '[times]', 'dimensions': []})
        self.inputs['values'] = Input({'name': 'Values', 'unit': '[values]', 'dimensions': []})

        self.outputs['times_out'] = Output({'name': 'Times', 'unit': '[times]', 'dimensions': []})
        self.outputs['values_out'] = Output({'name': 'Filtered values', 'unit': '[values]', 'dimensions': []})

        self.properties["filter"] = Property('', str, {'name': 'Serial dict filter', 'unit': 'dictname/5/dictname/...', 'dimensions': []})
        Property()

    async def func_peri(self, prep_to_peri=None):
        times = await self.get_input("times")
        values = await self.get_input("values")

        fil = self.get_property("filter")

        if fil is not '':
            fil = fil.split('/')
            for f in fil:
                try:
                    f = int(f)
                except:
                    pass
                values = values[f]

        self.set_output("times_out", times)
        self.set_output("values_out", values)
