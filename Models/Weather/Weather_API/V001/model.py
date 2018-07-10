from core import Supermodel
from core.util import Input, Output, Property
import csv
from datetime import datetime
from Models._utils.time import datetime2utc_time, utc_time2datetime
import pandas as pd
import numpy as np
from pytz import timezone
from scipy.interpolate import griddata
import json
import requests


# define the model class and inherit from class "Supermodel"
class Model(Supermodel):
    # model constructor
    def __init__(self, id, name: str):
        # instantiate supermodel
        super(Model, self).__init__(id, name)

        # define inputs

        # define outputs

        # define properties

        # define persistent variables

    async def func_birth(self):

        url_ad = "http://my.meteoblue.com/packages/basic-1h_solar-1h?apikey=137fcf8f8d26&lat=36.79&lon=-10.04&asl=0&temperature=C&windspeed=ms-1&format=json&tz=UTC"
        text = requests.get(url_ad).json()


    async def func_amend(self, keys=[]):
        pass

    async def func_peri(self, prep_to_peri=None):
        pass
