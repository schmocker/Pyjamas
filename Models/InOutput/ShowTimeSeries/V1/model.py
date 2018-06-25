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

        self.outputs['times'] = Output({'name': 'Times', 'unit': '[times]', 'dimensions': []})
        self.outputs['values'] = Output({'name': 'Filtered values', 'unit': '[values]', 'dimensions': []})

        self.properties["filter"] = Property('', str, {'name': 'Serial dict filter', 'unit': 'f1/f2/f3/...', 'dimensions': []})

    async def func_peri(self, prep_to_peri=None):
        times = await self.get_input("times")
        values = await self.get_input("values")

        filter = self.get_property("filter")

        if filter is not '':
            filter = filter.split('/')
            for f in filter:
                try:
                    f = int(f)
                except:
                    pass
                values = values[f]

        self.set_output("times", times)
        self.set_output("values", values)
