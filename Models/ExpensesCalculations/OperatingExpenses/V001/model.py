from pyjamas_core import Supermodel
from pyjamas_core.util import Input, Output, Property


# define the model class and inherit from class "Supermodel"
class Model(Supermodel):
    # model constructor
    def __init__(self, id, name: str):
        # instantiate supermodel
        super(Model, self).__init__(id, name)

        # define inputs
        self.inputs['AuslastungallerKWs'] = Input('CombinedLoad', info='combined load of all types of power plants, value[0-1]')
        self.inputs['KWDaten'] = Input('PowerPlantsData', unit='capex[€/W], spez_opex[1/s]', info='dict')

        # define outputs
        self.outputs['opex'] = Output('OPEX', unit='[€/J]')



    async def func_peri(self, prep_to_peri=None):
        # get inputs
        CombinedLoad = await self.get_input('AuslastungallerKWs')
        KWDaten = await self.get_input('KWDaten')

        OperationalExpenses = self.operatingexpenses(CombinedLoad, KWDaten)

        # set output
        self.set_output("opex", OperationalExpenses)


    # define additional methods (normal)
    def operatingexpenses(self, CombinedLoad, KWDaten):
        # Determine the operating expenses[$/J] of each power plant
        ################################################################################################################
        # Input Arguments:
        # CombinedLoad: Dictionary containing ids and load(Auslastung) of all power plants
        # -----------------
        #   id  Auslastung   Note: Incoming dictionary is not sorted and contains the load of wind turbines at first place
        # -----------------        on the top, then comes the load of PV, running-water, and storage power plants
        #   1    array(96)         respectively, in the last comes the load of remaining power plants(having 100% load).
        #   3    array(96)
        #   5    array(96)
        #   2    array(96)
        #   4    array(96)
        #   6    array(96)
        #   8    array(96)
        #   10   array(96)
        #   11   array(96)
        #
        # KWDaten: Dictionary holding the different parameters of power plants
        # ----------------------------------------------------------------------------------------------
        #   id  fk_kwt   kw_bezeichnung    power[W]          spez_info             Capex   Opex,  usw...
        # ----------------------------------------------------------------------------------------------
        #   1     2       Windturbine      1000000       NH: 150,  Z0: 0.03          1     0.01
        #   2     1      Photovoltaik      2000000       NH: 0,    Z0: {}            2     0.02
        #   3     2       Windturbine      3000000       NH: 200,  Z0: 0.2           3     0.03
        #   4     1      Photovoltaik      4000000       NH: 0,    Z0: {}            4     0.04
        #   5     2       Windturbine      5000000       NH: 250,  Z0: 0.03          5     0.05
        #   6     1      Photovoltaik      6000000       NH: 0,    Z0: {}            6     0.06
        #   8     3        Others          1000000       NH: 0,    Z0: {}            7     0.07
        #   10    3        Others          1000000       NH: 0,    Z0: {}            8     0.08
        #   11    4        Others          1000000       NH: 0,    Z0: {}            9     0.09
        # [KWID, FKKWT, KWBezeichnung, Power, Weitere spezifische parameter(Nabenhoehe, Z0, usw.), Capex,
        #  Opex, KEV, Brennstoffkosten, Entsorgungskostne, CO2-Kosten, usw.]
        #
        # Output Arguments:
        # opex: Dictionary containing power plant ids in one list and corresponding calculated operating
        # expenses of all power plant in other list
        # -----------------
        # id      opex   Note: Output dictionary is sorted according to the incoming id's of KWDaten.
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
        ################################################################################################################
        KWDatenID = KWDaten['id']

        def make_opex_for_one_plant(kw_id):
            index_of_kwid_in_CombinedLoad = CombinedLoad['power_plant_id'].index(kw_id)
            auslastung_for_kwid = CombinedLoad['load'][index_of_kwid_in_CombinedLoad]

            index_of_kwid_in_KWDaten = KWDaten['id'].index(kw_id)
            capex_for_kwid = KWDaten['capex'][index_of_kwid_in_KWDaten]
            opex_for_kwid = KWDaten['spez_opex'][index_of_kwid_in_KWDaten]
            expenses = capex_for_kwid * opex_for_kwid

            # boolean mask to avoid divide by zero
            boolmask = [(load!=0) for load in auslastung_for_kwid]

            # Function to avoid divide by zero
            def safedivide(bool, divider):
                if bool:
                    result = expenses / divider
                else:
                    result = 0
                return result

            Opex = [safedivide(val, divider=auslastung_for_kwid[idx]) for idx, val in enumerate(boolmask)]
            return Opex

        OpexForAllPlants = [make_opex_for_one_plant(id) for id in KWDatenID]

        opex = {'power_plant_id': KWDatenID, 'opex': OpexForAllPlants}
        return opex