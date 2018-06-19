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
        self.outputs['kw_data'] = Output({'name': 'PowerPlantData'})


        # define persistent variables
        self.kw_data = None

    async def func_birth(self):
        # Temporary dummy data for testing purpose, Will be replaced by the data coming from the database
        # KWDaten: Matrix holding different parameters of power plants
        # ------------------------------------------------------------------
        # KWIDs FKKWT    Power[W]    Nabenhöhe        Z0        Capex   Opex
        # ------------------------------------------------------------------
        #   1    2(WT)   1000000       150           0.03         1     0.01
        #   2    1(pv)   2000000        0          nothing =0     2     0.02
        #   3    2(WT)   3000000       200           0.03         3     0.03
        #   4    1(pv)   4000000        0          nothing =0     4     0.04
        #   5    2(WT)   5000000       250           0.03         5     0.05
        #   6    1(pv)   6000000        0          nothing =0     6     0.06
        #   8    3()     1000000        0          nothing =0     7     0.07
        #   10   3()     1000000        0          nothing =0     8     0.08
        #   11   4()     1000000        0          nothing =0     9     0.09
        # [KW-ID, FK-KWT, Power, Nabenhöhe, Weitere Parameter(Z0), Capex, Opex, KEV, Brennstoffkosten, Entsorgungskostne, CO2-Kosten]
        self.KWDaten = np.array([[1, 2, 1000000, 100, 0.03, 1, 0.01]
                                ,[2, 1, 2000000, 0,   0,    2, 0.02]
                                ,[3, 2, 3000000, 150, 0.2,  3, 0.03]
                                ,[4, 1, 4000000, 0,   0,    4, 0.04]
                                ,[5, 2, 5000000, 200, 0.03, 5, 0.05]
                                ,[6, 1, 6000000, 0,   0,    6, 0.06]
                                ,[8, 3, 1000000, 0,   0,    7, 0.07]
                                ,[10,3, 1000000, 0,   0,    8, 0.08]
                                ,[11,4, 1000000, 0,   0,    9, 0.09]])

    async def func_peri(self, prep_to_peri=None):

        # set output
        self.set_output("kw_data", self.KWDaten)



