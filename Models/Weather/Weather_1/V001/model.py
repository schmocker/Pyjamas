from core import Supermodel
from core.util import Input, Output, Property
import numpy as np
from pytz import timezone
import math
from datetime import date, timedelta
import json
from os import path


# define the model class and inherit from class "Supermodel"
class Model(Supermodel):
    # model constructor
    def __init__(self, id, name: str):
        # instantiate supermodel
        super(Model, self).__init__(id, name)

        # define inputs
        self.inputs['modus'] = Input(name='modus', unit='-', info="modus (live or simulation")
        self.inputs['KW'] = Input(name='KW_info', unit='-', info="KW information (id, lat, lon)")

        # define outputs
        self.outputs['weather_data'] = Output(name='weather data of KWs')

        # define properties
        self.properties['T_offset'] = Property(0, float, name='temperature offset', unit='%', info="offset of temperature in %")
        self.properties['w_offset'] = Property(0, float, name='wind speed offset', unit='%', info="offset of wind speed in %")
        self.properties['P_offset'] = Property(0, float, name='radiation offset', unit='%', info="offset of radiation in %")
        self.properties['ref_year'] = Property(0, float, name='reference year', unit='%', info="reference year for modeled weather")

        # define persistent variables
        self.model_pars = None

    # async def func_birth(self):
    #     pass


    # async def func_prep(self):
    #     # calculate something
    #     prep_result = 3 * 5
    #     # pass values to peri function
    #     return prep_result
    # ???????????? KW Daten vorbereiten / extrahieren?


    async def func_peri(self, prep_to_peri=None):
        # get inputs
        mode = await self.get_input('modus')
        # KW_data = await self.get_input('KW')

        # selection of weather model based on modus
        if mode=='live':
            weather_data = 1
        else:
            weather_data = 2


        # set output
        self.set_output("weather_data", weather_data)

