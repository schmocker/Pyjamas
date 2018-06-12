from core import Supermodel
from core.util import Input, Output, Property


# define the model class and inherit from class "Supermodel"
class Model(Supermodel):
    # model constructor
    def __init__(self, id, name: str):
        # instantiate supermodel
        super(Model, self).__init__(id, name)
        # define outputs
        self.outputs['kw_data'] = Output({'name': 'kw data'})


        # define persistent variables
        self.kw_data = None

    async def func_birth(self):
        self.kw_data = 5

    async def func_peri(self, prep_to_peri=None):

        # set output
        self.set_output("kw_data", self.kw_data)



