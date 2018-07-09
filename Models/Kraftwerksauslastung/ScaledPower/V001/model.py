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
        self.inputs['CombinedLoad'] = Input('CombinedLoad', info='value[0-1]')
        self.inputs['KWDaten'] = Input('PowerPlantsData', unit='W', info='Power extracted from PowerPlantData')

        # define outputs
        self.outputs['scaled_power'] = Output('Power', unit='W')

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
        # Determine the output power[W] of each power plant
        ###################################################################################################################
        # Input Arguments:
        # CombinedLoad: Dictionary containing KWIDs and load(Auslastung) of all power plants
        # -----------------
        # KWIDs  Auslastung   Note: Input matrix/dictionary is not sorted and contains the load of wind turbines at first place
        # -----------------         on the top, then comes the load of PV and in the last comes the load of remaining
        #   1    array(96)          power plants(having 100% load).
        #   3    array(96)
        #   5    array(96)
        #   2    array(96)
        #   4    array(96)
        #   6    array(96)
        #   8    array(96)
        #   10    array(96)
        #   11    array(96)
        #
        # KWDaten: Dictionary holding the different parameters of power plants
        # ------------------------------------------------------------------------------------
        #   id  fk_kwt   kw_bezeichnung    power[W]         spez_info             Capex   Opex
        # ------------------------------------------------------------------------------------
        #   1     2          WT            1000000       NH: 150,  Z0: 0.03         1     0.01
        #   2     1          PV            2000000       NH: 0,    Z0: {}           2     0.02
        #   3     2          WT            3000000       NH: 200,  Z0: 0.2          3     0.03
        #   4     1          PV            4000000       NH: 0,    Z0: {}           4     0.04
        #   5     2          WT            5000000       NH: 250,  Z0: 0.03         5     0.05
        #   6     1          PV            6000000       NH: 0,    Z0: {}           6     0.06
        #   8     3        OTHER           1000000       NH: 0,    Z0: {}           7     0.07
        #   10    3        OTHER           1000000       NH: 0,    Z0: {}           8     0.08
        #   11    4        OTHER           1000000       NH: 0,    Z0: {}           9     0.09
        # [KWID, FKKWT, KWBezeichnung, Power, Weitere spezifische parameter(Nabenhoehe, Z0, usw.), Capex, Opex, KEV, Brennstoffkosten, Entsorgungskostne, CO2-Kosten, usw.]
        #
        # Output Arguments:
        # ScaledPower: Dictionary containing KWIDs in the first column  and corresponding calculated
        # power of a power plant in following 96 columns
        # -----------------
        # id  Auslastung   Note: Output matrix is sorted according to the incoming id's of KWDaten.
        # -----------------
        #  1    array(96)
        #  2    array(96)
        #  3    array(96)
        #  4    array(96)
        #  5    array(96)
        #  6    array(96)
        #  8    array(96)
        #  10   array(96)
        #  11   array(96)
        ###################################################################################################################
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



