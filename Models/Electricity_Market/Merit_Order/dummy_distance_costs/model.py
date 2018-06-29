from core.util import Input, Output, Property
from core.supermodel import Supermodel
import numpy as np


class Model(Supermodel):

    def __init__(self, uuid, name:str):
        super(Model, self).__init__(uuid,name)
        self.outputs['data'] = Output(name='Data')

    async def func_peri(self, prep_to_peri=None):
        n_kw = 200
        n_dist = 3

        pp_ids = [i for i in range(n_kw)]
        np.random.shuffle(pp_ids)

        dist_ids = [i for i in range(n_dist)]
        np.random.shuffle(dist_ids)

        distance_costs = [(np.random.rand(n_dist) * 20).tolist() for i in pp_ids]

        data = {'power_plants': pp_ids,
                'distribution_networks': dist_ids,
                'costs': distance_costs}
        self.set_output("data", data)


if __name__ == "__main__":
    inputs = {}
    properties = {}
    outputs = Model.test(inputs, properties)
    print(outputs)
