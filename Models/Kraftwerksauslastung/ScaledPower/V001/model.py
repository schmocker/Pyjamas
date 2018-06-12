from core import Supermodel
from core.util import Input, Output, Property


# define the model class and inherit from class "Supermodel"
class Model(Supermodel):
    # model constructor
    def __init__(self, id, name: str):
        # instantiate supermodel
        super(Model, self).__init__(id, name)

        # define inputs
        self.inputs['power'] = Input({'name': 'Power'})
        self.inputs['load'] = Input({'name': 'Load'})

        # define outputs
        self.outputs['scaled_power'] = Output({'name': 'Power'})

    async def func_peri(self, prep_to_peri=None):
        # get inputs
        power = await self.get_input('power')
        load = await self.get_input('load')

        #### calculate

        # set output
        self.set_output("scaled_power", 99)


