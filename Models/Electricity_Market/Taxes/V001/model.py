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
        self.outputs['taxes'] = Output(name='Taxes', unit='€/J',
                                          info='Taxes')

        # define properties
        self.properties['tax'] = Property(default=0.1, data_type=float, name='taxes', unit='€/J',
                                          info="taxes", example='0.1')

        # define persistent variables
        self.taxes = None


    async def func_birth(self):
        await self.func_amend(['distNets'])

    async def func_amend(self, keys=[]):
        if 'tax' in keys:
            tax = self.get_property('tax')

            self.taxes = tax

    async def func_peri(self, prep_to_peri=None):
        self.set_output('taxes', self.taxes)
