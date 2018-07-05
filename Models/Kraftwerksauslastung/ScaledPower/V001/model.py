from core import Supermodel
from core.util import Input, Output, Property
import numpy as np


# define the model class and inherit from class "Supermodel"
class Model(Supermodel):
    # model constructor
    def __init__(self, id, name: str):
        # instantiate supermodel
        super(Model, self).__init__(id, name)

        # define inputs
        self.inputs['CombinedLoad'] = Input(name='CombinedLoad')
        self.inputs['KWDaten'] = Input(name='PowerPlantsData')

        # define outputs
        self.outputs['scaled_power'] = Output(name='Power')

    async def func_peri(self, prep_to_peri=None):
        # get inputs
        CombinedLoad = await self.get_input('CombinedLoad')
        KWDaten = await self.get_input('KWDaten')


        #### calculate
        ScaledPower = self.power(CombinedLoad, KWDaten)
        # set output
        self.set_output("scaled_power", ScaledPower)


    # define additional methods (normal)
    def power(self, CombinedLoad, KWDaten):
        KWDatenID = KWDaten['id']

        def make_power_for_one_plant(kw_id):

            index_of_kwid_in_CombinedLoad = CombinedLoad['id'].index(kw_id)
            auslastung_for_kwid = CombinedLoad['load'][index_of_kwid_in_CombinedLoad]
            auslastung = np.array(auslastung_for_kwid)
            index_of_kwid_in_KWDaten = KWDaten['id'].index(kw_id)
            power_for_kwid = KWDaten['power'][index_of_kwid_in_KWDaten]

            ScaledPowerOnePlant = power_for_kwid * auslastung
            return ScaledPowerOnePlant.tolist()

        ScaledPowerAllPlants = [make_power_for_one_plant(id) for id in KWDatenID]

        ScaledPower = {'id': KWDatenID, 'ScaledPower': ScaledPowerAllPlants}
        return ScaledPower



