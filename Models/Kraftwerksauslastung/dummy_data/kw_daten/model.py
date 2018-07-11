from core import Supermodel
from core.util import Input, Output, Property
import numpy as np


# define the model class and inherit from class "Supermodel"
class Model(Supermodel):
    # model constructor
    def __init__(self, id, name: str):
        # instantiate supermodel
        super(Model, self).__init__(id, name)
        # define outputs
        self.outputs['kw_data'] = Output('PowerPlantData')


        # define persistent variables
        self.kw_data = None

    async def func_birth(self):
        # Temporary dummy data for testing purpose, Will be replaced by the data coming from the database/ Kraftwerkspark
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

        self.KWDaten = {'id': [1, 2, 3, 4, 5, 6, 8, 10, 11, 12, 13, 14], 'fk_kwt': [2, 1, 2, 1, 2, 1, 5, 3, 3, 6, 4, 4],
             'kw_bezeichnung': ['WT','PV','WT','PV','WT','PV', 'Others', 'Laufwasserkraftwerk','Laufwasserkraftwerk','Others','Speicherwasserkraftwerk','Speicherwasserkraftwerk'],
             'power': [1000000, 2000000, 3000000, 4000000, 5000000, 6000000, 8000000, 10000000, 11000000, 12000000, 13000000, 14000000],
             'spez_info': [{'NH': 150, 'Z0': 0.03}, {}, {'NH': 100, 'Z0': 0.2}, {}, {'NH': 250, 'Z0': 0.03}, {}, {}, {}, {}, {}, {}, {},],
             'capex': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
             'opex': [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.12]}

    async def func_peri(self, prep_to_peri=None):

        # set output
        self.set_output("kw_data", self.KWDaten)



