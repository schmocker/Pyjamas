from core.util import Input, Output, Property
from core.supermodel import Supermodel
import numpy as np


class Model(Supermodel):

    def __init__(self, uuid, name:str):
        super(Model, self).__init__(uuid,name)
        self.outputs['data'] = Output(name='Data')
        self.inputs['n_kw'] = Input(name='n_kw')
        self.inputs['dns'] = Input(name='DistNets')

    async def func_peri(self, prep_to_peri=None):
        n_kw = await self.get_input("n_kw")
        n_kw = int(n_kw)
        dns = await self.get_input("dns")
        dn_ids = dns['dist_networks']
        n_dist = len(dn_ids)

        pp_ids = [i for i in range(n_kw)]
        np.random.shuffle(pp_ids)

        distance_costs = [(np.random.rand(n_dist) * 20).tolist() for i in pp_ids]

        data = {'power_plants': pp_ids,
                'distribution_networks': dn_ids,
                'costs': distance_costs}
        self.set_output("data", data)


if __name__ == "__main__":
    inputs = {}
    properties = {}
    outputs = Model.test(inputs, properties)
    print(outputs)
