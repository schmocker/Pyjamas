from pyjamas_core import Supermodel
from pyjamas_core.util import Input, Output, Property
import numpy as np
from datetime import datetime as dt
from Models._utils.time import utc_time2datetime, datetime2utc_time


# define the model class and inherit from class "Supermodel"
class Model(Supermodel):
    # model constructor
    def __init__(self, id, name: str):
        # instantiate supermodel
        super(Model, self).__init__(id, name)

        # define inputs
        self.inputs['futures'] = Input('Futures', unit='s', info='utc time array in seconds since epoch')
        self.inputs['kwDaten'] = Input('PowerPlantsData', info='dict, power plant id required')

        # define outputs
        self.outputs['load'] = Output('Load', info='load of all running-water power plants, value[0-1]')

        self.ref_year = 2016
        ref_dates = [[self.ref_year, 1, 1],   [self.ref_year, 1, 8],   [self.ref_year, 1, 12],  [self.ref_year, 1, 17],  [self.ref_year, 1, 26],
                     [self.ref_year, 2, 1],   [self.ref_year, 2, 8],   [self.ref_year, 2, 10],  [self.ref_year, 2, 12],  [self.ref_year, 2, 14], [self.ref_year, 2, 20], [self.ref_year, 2, 26],
                     [self.ref_year, 3, 1],   [self.ref_year, 3, 6],   [self.ref_year, 3, 14],  [self.ref_year, 3, 28],
                     [self.ref_year, 4, 7],   [self.ref_year, 4, 11],  [self.ref_year, 4, 19],  [self.ref_year, 4, 22],  [self.ref_year, 4, 24], [self.ref_year, 4, 30],
                     [self.ref_year, 5, 2],   [self.ref_year, 5, 8],   [self.ref_year, 5, 11],  [self.ref_year, 5, 13],  [self.ref_year, 5, 22],
                     [self.ref_year, 6, 1],
                     [self.ref_year, 7, 7],   [self.ref_year, 7, 10],  [self.ref_year, 7, 13],  [self.ref_year, 7, 20],  [self.ref_year, 7, 30],
                     [self.ref_year, 8, 4],   [self.ref_year, 8, 5],   [self.ref_year, 8, 7],   [self.ref_year, 8, 16],  [self.ref_year, 8, 19],
                     [self.ref_year, 9, 4],   [self.ref_year, 9, 6],   [self.ref_year, 9, 18],  [self.ref_year, 9, 19],
                     [self.ref_year, 10, 14], [self.ref_year, 10, 24], [self.ref_year, 10, 26],
                     [self.ref_year, 11, 4],  [self.ref_year, 11, 6],  [self.ref_year, 11, 9],  [self.ref_year, 11, 11], [self.ref_year, 11, 16], [self.ref_year, 11, 19],
                     [self.ref_year, 12, 1],  [self.ref_year, 12, 11], [self.ref_year, 12, 18], [self.ref_year, 12, 1],
                     [self.ref_year + 1, 1, 1]]
        self.ref_dates = np.array([datetime2utc_time(dt(d[0], d[1], d[2])) for d in ref_dates])
        self.ref_loads = np.array([0.300, 0.512,  1.0,   0.5447, 0.432,
                                   1,     0.748,  0.834, 0.742,  0.8473, 0.6227, 0.7887,
                                   0.674, 0.8247, 0.541, 0.431,
                                   0.646, 0.5747, 1.0,   0.8,    0.9687, 0.778,
                                   0.925, 0.6827, 0.682, 1.0,    0.994,
                                   1.0,
                                   1.0,   0.882,  1.0,   1.0,    0.827,
                                   0.774, 1.0,    1.0,   0.742,  0.805,
                                   0.550, 0.77,   0.524, 0.552,
                                   0.328, 0.336,  0.542,
                                   0.372, 0.534,  0.49, 0.762, 0.534, 0.704,
                                   0.425, 0.340,  0.316, 0.284,
                                   0.300])


    async def func_peri(self, prep_to_peri=None):
        # get inputs
        futures = await self.get_input('futures')
        kwDaten = await self.get_input('kwDaten')

        load = self.laufwasserKWauslastung(kwDaten, futures)

        # set output
        self.set_output("load", load)


    # define additional methods (normal)
    def laufwasserKWauslastung(self, KWDaten, Futures):
        # Determine the load(Auslastung) running water power plant
        ###################################################################################################################
        # Input Arguments:
        # KWDaten: Dictionary holding the different parameters of power plants
        # ----------------------------------------------------------------------------------------------
        #   id  fk_kwt   kw_bezeichnung    power[W]          spez_info             Capex   Spez_Opex,  usw...
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
        #  Spez_Opex, KEV, Brennstoffkosten, Entsorgungskostne, CO2-Kosten, usw.]
        #
        # Futures: Incoming datetime values (produced by Scheduler/Cronjob/V2), required for interpolation
        #
        # Output Arguments:
        # Auslastung: Dictionary containing Power plant IDs(id) in the first list and corresponding calculated
        # load(Auslastung) of running-water power plants in second list, output values are between [0-1] except ids
        # ---------------------------
        #   id   Auslastung   Note: Output matrix contains the load of running water power plants only
        # ---------------------------
        #   10    array(96)
        #   11    array(96)
        ###################################################################################################################
        KWBezeichnung = 'Laufwasserkraftwerk'  # ForeignKeyKWTyp = 1  # ForeignKey Kraftwerkstyp z.B. 1= PV-Anlage, 2= WindKraftwerk
        KWDaten = np.array([KWDaten['id'], KWDaten['bez_kraftwerkstyp'], KWDaten['spez_info']]).transpose()

        # Extracting data corresponding solely to running water power plant
        KraftwerksDaten = KWDaten[KWDaten[:, 1] == KWBezeichnung]

        def make_load_for_one_plant():

            futures = [utc_time2datetime(f).replace(year=self.ref_year) for f in Futures]
            futures = [datetime2utc_time(f) for f in futures]
            # One-dimensional linear interpolation
            load = np.interp(futures, self.ref_dates, self.ref_loads).tolist()
            return load

        KWid = [kw[0] for kw in KraftwerksDaten]
        loads = [make_load_for_one_plant() for kw in KraftwerksDaten]

        Auslastung = {'power_plant_id': KWid, 'load': loads}
        return Auslastung


# For testing purposes
if __name__ == "__main__":
    kw_daten = {'id': [1, 2, 3, 4, 5, 6, 8, 10, 11], 'fk_kwt': [2, 1, 2, 1, 2, 1, 5, 3, 4],
             'kw_bezeichnung': ['WT','PV','WT','PV','WT','PV','Laufwasserkraftwerk','Laufwasserkraftwerk','OTHER'],
             'power': [1000000, 2000000, 3000000, 4000000, 5000000, 6000000, 8000000, 9000000, 7000000],
             'spez_info': [{'NH': 150, 'Z0': 0.03}, {}, {'NH': 100, 'Z0': 0.2}, {}, {'NH': 250, 'Z0': 0.03}, {}, {}, {}, {}],
             'capex': [1, 2, 3, 4, 5, 6, 7, 8, 9],
             'spez_opex': [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09]}

    Props={}
    Inputs = {
        'futures': [1531227300, 1531227400, 1531227500, 1531227600],
        'kwDaten': kw_daten
    }
    Output = Model.test(Inputs, Props)

    print(Output)