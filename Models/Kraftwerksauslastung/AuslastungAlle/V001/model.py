from core import Supermodel
from core.util import Input, Output, Property


# define the model class and inherit from class "Supermodel"
class Model(Supermodel):
    # model constructor
    def __init__(self, id, name: str):
        # instantiate supermodel
        super(Model, self).__init__(id, name)

        # define inputs
        self.inputs['WTAuslastung'] = Input({'name': 'LoadWT'})
        self.inputs['PVAuslastung'] = Input({'name': 'LoadPV'})
        self.inputs['KWDaten'] = Input({'name': 'PowerPlantsData'})

        # define outputs
        self.outputs['GemeinsameAuslastung'] = Output({'name': 'LoadMatrix'})

    async def func_peri(self, prep_to_peri=None):
        # get inputs
        WTAuslastung = await self.get_input('WTAuslastung')
        PVAuslastung = await self.get_input('PVAuslastung')
        KWDaten = await self.get_input('KWDaten')

        #### calculate

        # set output
        self.set_output("GemeinsameAuslastung", PVAuslastung)


