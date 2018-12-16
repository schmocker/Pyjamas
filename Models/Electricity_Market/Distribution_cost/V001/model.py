from pyjamas_core import Supermodel
from pyjamas_core.util import Input, Output, Property
import numpy as np
import json

# define the model class and inherit from class "Supermodel"
class Model(Supermodel):
    # model constructor
    def __init__(self, id, name: str):
        # instantiate supermodel
        super(Model, self).__init__(id, name)

        # define inputs
        self.inputs['dist_net'] = Input(name='Distribution networks', unit='{-, {Grad, Grad}}', info='distribution networks')

        # define outputs
        self.outputs['dist_cost'] = Output(name='Distribution cost', unit='€/J', info='distribution cost')

        # define properties
        cost_constant_def = 36000
        cost_constant_def = json.dumps(cost_constant_def)
        self.properties['cost_const'] = Property(default=cost_constant_def, data_type=str, name='constant dist cost', unit='€/km*MWh', info='constant distribution costs', example='36000')

        # persistent variables
        self.cost_constant = None

    async def func_birth(self):
        pass

    async def func_amend(self, keys=[]):

        cost_str = self.get_property('cost_const')
        cost = json.loads(cost_str)
        # [€/km*MWh] to [€/m*J] (SI Units)
        self.cost_constant = cost/3.6e12

    async def func_peri(self, prep_to_peri=None):

        # locations information
        dist_nets = await self.get_input('dist_net')
        dist_loc = dist_nets['dist_networks']

        # costs
        cost_vec = []
        for ni in range(0, len(dist_loc)):

            cost_i = self.cost_constant
            cost_vec.append(cost_i)

        # output
        output = {'distribution_networks': dist_loc,
                  'costs': cost_vec}

        # set output
        self.set_output("dist_cost", output)

if __name__ == "__main__":

    # input
    # distnets = {"Baden": {"Lat": 47.47256, "Lon": 8.30850},
    #             "Brugg": {"Lat": 47.48420, "Lon": 8.20706},
    #             "Olten": {"Lat": 47.35212, "Lon": 7.90801}}
    distnets = {"dist_networks": ["Baden", "Brugg", "Olten"],
                "Latitude": [47.47256, 47.48420, 47.35212],
                "Longitude": [8.30850, 8.20706, 7.90801]}
    distnets = json.dumps(distnets)

    future_vec = [1531746402, 1531746403, 1531746404, 1531746405]

    # properties
    costs_const = [100, 110, 120]
    costs_const = json.dumps(costs_const)

    inputs = {'dist_net': distnets,
              'futures': future_vec}
    props = {'cost_const': costs_const}

    outputs = Model.test(inputs, props)
