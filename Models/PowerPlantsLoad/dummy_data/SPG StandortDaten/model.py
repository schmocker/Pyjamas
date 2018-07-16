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
        self.outputs['standorte'] = Output('StandorteSPG')


        # define persistent variables
        self.kw_data = None

    async def func_birth(self):

        self.standorte = {"Baden": {"Lat": 47.47256, "Lon": 8.30850},
                          "Brugg": {"Lat": 47.48420, "Lon": 8.20706},
                          "Olten": {"Lat": 47.35212, "Lon": 7.90801}}


    async def func_peri(self, prep_to_peri=None):

        # set output
        self.set_output("standorte", self.standorte)



