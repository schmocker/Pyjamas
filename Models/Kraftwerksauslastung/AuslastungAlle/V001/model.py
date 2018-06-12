from core import Supermodel
from core.util import Input, Output, Property


# define the model class and inherit from class "Supermodel"
class Model(Supermodel):
    # model constructor
    def __init__(self, id, name: str):
        # instantiate supermodel
        super(Model, self).__init__(id, name)

        # define inputs
        self.inputs['kw_data'] = Input({'name': 'Kraftwerksdaten'})
        self.inputs['load_PV'] = Input({'name': 'Auslastung PV'})
        self.inputs['load_WT'] = Input({'name': 'Auslastung WT'})

        # define outputs
        self.outputs['load'] = Output({'name': 'Auslastung'})

    async def func_peri(self, prep_to_peri=None):
        # get inputs
        kw_data = await self.get_input('kw_data')
        load_PV = await self.get_input('load_PV')
        load_WT = await self.get_input('load_WT')

        #### calculate

        # set output
        self.set_output("load", 6)


