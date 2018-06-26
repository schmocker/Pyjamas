import asyncio
from core.util import Input, Output, Property
from core.supermodel import Supermodel
import json


class Model(Supermodel):
    """
        plot time series
    """

    def __init__(self, uuid, name :str):
        super(Model, self).__init__(uuid,name)

        self.inputs['times'] = Input({'name': 'Times', 'unit': '[times]', 'dimensions': []})
        self.inputs['values'] = Input({'name': 'Values', 'unit': '[values]', 'dimensions': []})

        self.outputs['times_out'] = Output({'name': 'Times', 'unit': '[times]', 'dimensions': []})
        self.outputs['values_out'] = Output({'name': 'Filtered values', 'unit': '[values]', 'dimensions': []})

        self.properties["filter"] = Property('', str, {'name': 'Serial dict and array filter for values', 'unit': '"dictname", 3, ...', 'dimensions': []})

    async def func_peri(self, prep_to_peri=None):
        times = await self.get_input("times")
        values = await self.get_input("values")

        fil = self.get_property("filter")
        fil = json.loads('[' + fil + ']')
        for f in fil:
            values = values[f]

        self.set_output("times_out", times)
        self.set_output("values_out", values)


if __name__ == "__main__":
    inputs = {
        'times': [1,2,3,4],
        'values': {'hallo': [[4,5,6,7],[4,5,6,7],[4,5,6,7]], 'du': [9,8,7,6]}
    }

    properties = {
        'filter': '"hallo" ,2'
    }

    outputs = Model.test(inputs, properties)

    print(outputs)
