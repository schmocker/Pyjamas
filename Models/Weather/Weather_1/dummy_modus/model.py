from core import Supermodel
from core.util import Input, Output


# define the model class and inherit from class "Supermodel"
class Model(Supermodel):
    # model constructor
    def __init__(self, id, name: str):
        # instantiate supermodel
        super(Model, self).__init__(id, name)

        # define inputs
        # self.inputs['step'] = Input(name='step')

        # define outputs
        self.outputs['modus'] = Output(name='modus')


    async def func_peri(self, prep_to_peri=None):

        mode = "live"
        # mode = "simulation"

        # set output
        self.set_output("modus", mode)
