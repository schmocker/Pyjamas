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
        self.inputs['opex'] = Input('OPEX', info='dict')
        self.inputs['KWDaten'] = Input('PowerPlantsData', info='dict')

        # define outputs
        self.outputs['Grenzkosten'] = Output('MarginalCost')



    async def func_peri(self, prep_to_peri=None):
        # get inputs
        OPEX = await self.get_input('opex')
        KWDaten = await self.get_input('KWDaten')

        Grenzkosten = self.marginalcost(OPEX, KWDaten)

        # set output
        self.set_output("Grenzkosten", Grenzkosten)


    # define additional methods (normal)
    def marginalcost(self, OPEX, KWDaten):
        # Determine the output power[W] of each power plant
        ###################################################################################################################
        # Input Arguments:
        # OPEX: Dictionary containing KWIDs and operating expenses of all power plants
        # -----------------
        # KWIDs  Auslastung   Note: Input matrix/dictionary is sorted according to KWDaten
        # -----------------
        #   1    array(96)
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
        # Grenzkosten: Dictionary containing KWIDs in the first column  and corresponding calculated
        # marginal cost for a power plant in following 96 columns
        # -----------------
        # id   Grenzkosten   Note: Output matrix is sorted according to the incoming id's of KWDaten.
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

        def make_cost_for_one_plant(kw_id):
            index_of_kwid_in_OPEX = OPEX['id'].index(kw_id)
            OPEX_for_kwid = OPEX['opex'][index_of_kwid_in_OPEX]
            OPEXP = np.array(OPEX_for_kwid)
            index_of_kwid_in_KWDaten = KWDaten['id'].index(kw_id)
            brennstoffkosten_for_kwid = KWDaten['brennstoffkosten'][index_of_kwid_in_KWDaten]
            co2kosten_for_kwid = KWDaten['co2kosten'][index_of_kwid_in_KWDaten]
            entsorgungskosten_for_kwid = KWDaten['entsorgungskosten'][index_of_kwid_in_KWDaten]
            kev_for_kwid = KWDaten['kev'][index_of_kwid_in_KWDaten]
            KEV = np.array(kev_for_kwid)

            Grenzkosten = OPEXP + brennstoffkosten_for_kwid + co2kosten_for_kwid + entsorgungskosten_for_kwid - KEV
            return Grenzkosten.tolist()

        GrenzkostenForAllPlants = [make_cost_for_one_plant(id) for id in KWDatenID]

        Grenzkosten = {'id': KWDatenID, 'Grenzkosten': GrenzkostenForAllPlants}
        return Grenzkosten