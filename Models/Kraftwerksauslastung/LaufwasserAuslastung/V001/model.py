from core import Supermodel
from core.util import Input, Output, Property
import numpy as np
import random
from datetime import datetime as dt
from Models._utils.time import utc_time2datetime, datetime2utc_time

# define the model class and inherit from class "Supermodel"
class Model(Supermodel):
    # model constructor
    def __init__(self, id, name: str):
        # instantiate supermodel
        super(Model, self).__init__(id, name)

        # define inputs
        self.inputs['futures'] = Input('Futures', info='dict')
        self.inputs['kwDaten'] = Input('PowerPlantsData', info='dict')

        # define outputs
        self.outputs['load'] = Output('Load', info='value[0-1]')

        self.ref_year = 2018
        ref_dates = [[self.ref_year, 1, 1], [self.ref_year, 4, 1], [self.ref_year, 8, 1], [self.ref_year + 1, 1, 1]]
        self.ref_dates = np.array([datetime2utc_time(dt(d[0], d[1], d[2])) for d in ref_dates])
        self.ref_loads = np.array([0.3, 0.5, 1, 0.3])


    async def func_peri(self, prep_to_peri=None):
        # get inputs
        futures = await self.get_input('futures')
        kwDaten = await self.get_input('kwDaten')


        load = self.laufwasserauslastung(kwDaten, futures)

        # set output
        self.set_output("load", load)



    # define additional methods (normal)
    def laufwasserpowerplant(self, WaterFlowRate):
        # Simulates a dummy running water power plant for specified incoming values
        ###################################################################################################################
        # Input Arguments:
        # WaterFlowRate: Measured values
        #
        # Output Arguments:
        # Auslastung: Calculated load(Auslastung), output values are between [0-1]
        ###################################################################################################################

        # Generates random numbers between 0 & 100
        #PowerOutput = random.sample(range(0, 100), WaterFlowRate.shape[1])
        PowerOutput = random.sample(range(0, 100), len(WaterFlowRate))
        Auslastung = [(num / 100) for num in PowerOutput]

        return Auslastung


    def laufwasserauslastung(self, KWDaten, Futures):
        # Determine the load(Auslastung) running water power plant
        ###################################################################################################################
        # Input Arguments:
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
        # WetterDaten: Dictionary holding Power plant IDs(KWIDs) and weather data for all types of power plants
        # ----------------------------------------------
        #  id      windspeed   radiation   windmesshoehe
        # ----------------------------------------------
        #  1(WT)   array(96)   None            50
        #  2(PV)   None        array(96)       None
        #  3(WT)   array(96)   None            45
        #  4(PV)   None        array(96)       None
        #  5(WT)   array(96)   None            80
        #  6(PV)   None        array(96)       None
        #  8       None        None            None
        #  10      None        None            None
        #  11      None        None            None
        #
        # Output Arguments:
        # PVAuslastung: Dictionary containing KWIDs in the first column  and corresponding calculated
        # load(Auslastung) of PV power plant in following 96 columns, output values are between [0-1] except KWIDs
        # -----------------
        # KWIDs  Auslastung   Note: Output matrix contains only load for PV power plants
        # -----------------
        #   2    array(96)
        #   4    array(96)
        #   6    array(96)
        ###################################################################################################################
        KWBezeichnung = 'Laufwasserkraftwerk'  # ForeignKeyKWTyp = 1  # ForeignKey Kraftwerkstyp z.B. 1= PV-Anlage, 2= WindKraftwerk
        KWDaten = np.array([KWDaten['id'], KWDaten['kw_bezeichnung'], KWDaten['spez_info']]).transpose()

        # Extracting data corresponding solely to running water power plant
        KraftwerksDaten = KWDaten[KWDaten[:, 1] == KWBezeichnung]

        def make_load_for_one_plant():
            #index_of_kwid_in_wetter = WetterDaten['id'].index(kw_id)
            #laufwasserdaten_for_kwid = WetterDaten['laufwasserdaten'][index_of_kwid_in_wetter]
            #laufwasserdaten = np.array(laufwasserdaten_for_kwid)
            #laufwasserdaten = laufwasserdaten_for_kwid

            futures = [utc_time2datetime(f).replace(year=self.ref_year) for f in Futures]
            futures = [datetime2utc_time(f) for f in futures]
            loads = np.interp(futures, self.ref_dates, self.ref_loads).tolist()
            return loads

            # laufwasserdaten = Futures

            # auslastung = self.laufwasserpowerplant(laufwasserdaten)
            # return auslastung

        KWid = [kw[0] for kw in KraftwerksDaten]
        load = [make_load_for_one_plant() for kw in KraftwerksDaten]

        LaufwasserAuslastung = {'id': KWid, 'load': load}

        return LaufwasserAuslastung


if __name__ == "__main__":
    kw_daten = {'id': [1, 2, 3, 4, 5, 6, 8, 10, 11], 'fk_kwt': [2, 1, 2, 1, 2, 1, 5, 3, 4],
             'kw_bezeichnung': ['WT','PV','WT','PV','WT','PV','Laufwasserkraftwerk','Laufwasserkraftwerk','OTHER'],
             'power': [1000000, 2000000, 3000000, 4000000, 5000000, 6000000, 8000000, 9000000, 7000000],
             'spez_info': [{'NH': 150, 'Z0': 0.03}, {}, {'NH': 100, 'Z0': 0.2}, {}, {'NH': 250, 'Z0': 0.03}, {}, {}, {}, {}],
             'capex': [1, 2, 3, 4, 5, 6, 7, 8, 9],
             'opex': [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09]}

    Props={}
    Inputs = {
        'futures': [1531227300, 1531227400, 1531227500, 1531227600],
        'kwDaten': kw_daten
    }
    Output = Model.test(Inputs, Props)

    print(Output)