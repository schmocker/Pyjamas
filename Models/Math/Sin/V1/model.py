import asyncio
from core.util import Input, Output, Property
from core.supermodel import Supermodel
import numpy as np

class Model(Supermodel):
    """
        sets the sum of 3 inputs as output
    """

    def __init__(self, uuid, name: str):
        super(Model, self).__init__(uuid,name)

        self.inputs['in'] = Input(name='Numbers', unit='any', info='number or number array')

        self.outputs['sin'] = Output(name='Sin', unit='any', info='number or number array')

    async def func_peri(self, prep_to_peri=None):

        nums = await self.get_input('in')

        nums = np.array(nums)

        sin = np.sin(nums)

        self.set_output("sin", sin.tolist())

if __name__=='__main__':
    inputs = {
        'in': 1
    }

    properties = {}

    outputs = Model.test(inputs, properties)

    print(outputs)
