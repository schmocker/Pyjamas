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
        self.outputs['KW_data'] = Output(name='KW info')


    async def func_peri(self, prep_to_peri=None):

        list_key = ["ID", "Longitude", "Latidude"]
        list_ID = [1, 2, 3, 4]
        list_long = [-5, 5, 10, 20]
        list_lat = [40, 45, 50, 52.5]

        data_KW = dict(zip(list_key, [list_ID, list_long, list_lat]))

        # set output
        self.set_output("KW_data", data_KW)
