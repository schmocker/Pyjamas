from core.util import Input, Output, Property
from core.supermodel import Supermodel
import numpy as np


class Model(Supermodel):

    def __init__(self, uuid, name:str):
        super(Model, self).__init__(uuid,name)
        self.outputs['data'] = Output(name='Data')

    async def func_peri(self, prep_to_peri=None):
        n_ts = 96
        n_kw = 200

        pp_ids = [i for i in range(n_kw)]
        np.random.shuffle(pp_ids)

        marginal_costs = [(np.random.rand(n_ts) * 50 + 5).tolist() for i in pp_ids]

        data = {'power_plants': pp_ids,
                'costs': marginal_costs}
        self.set_output("data", data)


if __name__ == "__main__":
    inputs = {}
    properties = {}
    outputs = Model.test(inputs, properties)
    print(outputs)
