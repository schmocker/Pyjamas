from core.util import Input, Output, Property
from core.supermodel import Supermodel
import numpy as np


class Model(Supermodel):

    def __init__(self, uuid, name :str):
        super(Model, self).__init__(uuid,name)
        self.outputs['data'] = Output(name='Data')
        self.inputs['fut'] = Input(name='Futures')

    async def func_peri(self, prep_to_peri=None):
        fut = await self.get_input("fut")
        n_ts = len(fut)
        demands = (np.random.rand(n_ts) * 500 + 250).tolist()
        self.set_output("data", demands)


if __name__ == "__main__":
    inputs = {}
    properties = {}
    outputs = Model.test(inputs, properties)
    print(outputs)