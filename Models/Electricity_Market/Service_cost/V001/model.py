from core import Supermodel
from core.util import Input, Output, Property
import json


# define the model class and inherit from class "Supermodel"
class Model(Supermodel):
    # model constructor
    def __init__(self, id, name: str):
        # instantiate supermodel
        super(Model, self).__init__(id, name)

        # define inputs

        # define outputs
        self.outputs['service_cost'] = Output(name='Service costs', unit='€/J',
                                          info='Service costs')

        # define properties
        self.properties['serv_cost'] = Property(default=15000, data_type=float, name='service costs', unit='€/J',
                                          info="service costs", example='0.15')

        # define persistent variables
        self.service_cost = None


    async def func_birth(self):
        await self.func_amend(['serv_cost'])

    async def func_amend(self, keys=[]):
        if 'serv_cost' in keys:
            serv_cost = self.get_property('serv_cost')
            self.service_cost = serv_cost

    async def func_peri(self, prep_to_peri=None):
        self.set_output('service_cost', self.service_cost)
