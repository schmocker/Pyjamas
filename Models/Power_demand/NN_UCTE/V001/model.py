from pyjamas_core import Supermodel
from pyjamas_core.util import Input, Output, Property
import numpy as np
from pytz import timezone
import math
from datetime import date, timedelta
import json
from Models._utils.time import datetime2utc_time, utc_time2datetime
import os

# define the model class and inherit from class "Supermodel"
class Model(Supermodel):
    # model constructor
    def __init__(self, id, name: str):
        # instantiate supermodel
        super(Model, self).__init__(id, name)

        # define inputs
        self.inputs['futures'] = Input(name='Futures', unit='s', info="time array in utc [s]")
        self.inputs['demand_weather'] = Input(name='Weather for demand calculation', unit='dict {id, lat, lon, temperature}', info="Weather for demand calculation")
        self.inputs['demand_loc'] = Input(name='Demand locations', unit='id, lat, long', info="Demand locations (one location per country)")

        # define outputs
        self.outputs['p_dem'] = Output(name='Power demand', unit='W', info="power demand of UCTE in W")

        # define properties
        self.properties['offset'] = Property(default=0, data_type=float, name='demand offset', unit='%', info="offset of demand in %", example='100: doubles the value')

        # define persistent variables
        self.model_para = None

    async def func_birth(self):

        # read model parameters of the neural network from file

        path = os.path.abspath(__file__)
        dir_path = os.path.dirname(path)
        filename = os.path.join(dir_path, 'confidential', 'model_parameter_GW_LK_20.txt')
        with open(filename, "r") as f:
            json_str = f.read()
            data = json.loads(json_str)
        self.model_para = data

    async def func_peri(self, prep_to_peri=None):

        # get inputs
        dates = await self.get_input('futures')
        demand_weather = await self.get_input('demand_weather')
        demand_loc = await self.get_input('demand_loc')

        # data preparation to input format for neural network
        # - extract date information
        date_mat = [self.prep_date(item) for item in dates]
        # - add temperature and country information
        NN_input = self.prep_temp(date_mat, demand_weather, demand_loc)

        # calculation by neural network frame
        demand = self.calc_demand(NN_input)

        # set output
        self.set_output("p_dem", demand)

    @staticmethod
    def prep_date(dates):

        # change time format from utc to datetime and add timezone information
        date_datetime = utc_time2datetime(dates)
        date_UTC = date_datetime.replace(tzinfo=timezone('UTC'))
        date_local = date_UTC.astimezone(timezone('Europe/Brussels'))

        # determine day of year
        day_year = (date(date_local.year, date_local.month, date_local.day)-date(date_local.year, 1, 1)).days+1
        # determination if weekend or not
        weekend = int((date_local.isoweekday() == 6 | date_local.isoweekday() == 7) is True)
        # calculate seconds of the day
        seconds = date_local.hour * 3600 + date_local.minute * 60
        # determination of holiday or not (christmas, eastern)
        holiday = Model.func_holiday(date_local)

        # array by properties year, weekend, seconds and holiday
        date_pred = [day_year, weekend, seconds, holiday]

        return date_pred

    @staticmethod
    def prep_temp(date_mat, demand_weather, demand_loc):

        # date
        date_mat = np.array(date_mat)
        nn_date = np.tile(date_mat, (demand_loc['id'].__len__(), 1))

        # country
        country_vec = np.repeat(demand_loc['id'], date_mat.shape[0])
        country_vec = country_vec[:, np.newaxis]

        # temperature
        temp_vec = np.array(demand_weather['temperature'])
        temp_vec = np.reshape(temp_vec, -1)
        temp_vec = temp_vec[:, np.newaxis]

        # concatenate
        nn_input = np.concatenate((nn_date, temp_vec, country_vec), axis=1)

        return nn_input

    def calc_demand(self, nn_input):

        # calculation of demand [GW] per date and country
        demand_GW_i = self.func_NeuralNetwork(nn_input)

        # summarize per date over countries
        num_country = np.unique(nn_input[:, 5])
        demand_reshape = demand_GW_i.reshape((num_country.size, -1))
        demand_GW = np.sum(demand_reshape, axis=0)

        # offset
        demand_GW = np.multiply(demand_GW,(1+self.get_property('offset')/100))

        # convert GW to W
        demand = np.multiply(demand_GW, 1e9)

        return demand.tolist()

    def func_NeuralNetwork(self, x1):

        # model parameter
        model_para = self.model_para

        # ===== NEURAL NETWORK CONSTANTS =====

        # - Input 1
        x1_step1 = model_para['x1_step1']
        # - Layer 1
        b1 = np.array(model_para['b1'])
        b1 = b1[np.newaxis, :]
        b1 = np.transpose(b1)
        IW1_1 = np.array(model_para['IW1_1'])
        # - Layer 2
        b2 = np.array(model_para['b2'])
        LW2_1 = np.array(model_para['LW2_1'])
        # - Output 1
        y1_step1 = model_para['y1_step1']

        # ===== SIMULATION ========

        # Dimensions
        Q = x1.shape[0]

        # Input 1
        x1 = np.transpose(x1)
        xp1 = self.mapminmax_apply(x1, x1_step1)

        # Layer 1
        a1 = self.tansig_apply(np.tile(b1, (1, Q)) + np.matmul(IW1_1, xp1))

        # Layer 2
        a2 = np.tile(b2, (1, Q)) + np.matmul(LW2_1, a1)

        # Output 1
        y1 = self.mapminmax_reverse(a2, y1_step1)

        return y1

    @staticmethod
    def mapminmax_apply(a, x1_step1):

        atilde = np.transpose(a)
        y = np.add(atilde, -np.array(x1_step1['xoffset']))
        y = y * np.array(x1_step1['gain'])
        y = y + np.array(x1_step1['ymin'])
        y = np.transpose(y)

        return y

    @staticmethod
    def tansig_apply(n):

        a = 2 / (1 + np.exp(-2 * n)) - 1

        return a

    @staticmethod
    def mapminmax_reverse(a, y1_step1):

        x = a - np.array(y1_step1['ymin'])
        x = x / np.array(y1_step1['gain'])
        x = x + np.array(y1_step1['xoffset'])

        return x

    @staticmethod
    def func_holiday(date_x):

        # eastern
        hday_1 = Model.func_easterday(date_x)

        # christmas
        hday_2 = Model.func_xmasday(date_x)

        # holidays
        holidays = int((hday_1 | hday_2) is True)

        return holidays

    @staticmethod
    def func_easterday(date_x):

        # determine easter sunday of the date year
        year = date_x.year
        ret_eastersun = Model.func_eastersunday(year)
        d_eastersun = date(year, ret_eastersun[1], ret_eastersun[0])

        # determine good friday and easter monday
        easter_start = d_eastersun - timedelta(days=2)
        easter_end = d_eastersun + timedelta(days=1)

        # set days from good friday till easter monday to true
        easterday = int(((easter_start <= date_x.date()) & (date_x.date() <= easter_end)) is True)

        return easterday

    @staticmethod
    def func_eastersunday(year_x):

        # easter formula based on Heiner Lichtenberg
        k = math.floor(year_x / 100)
        m = 15 + math.floor((3 * k + 3) / 4) - math.floor((8 * k + 13) / 25)
        s = 2 - math.floor((3 * k + 3) / 4)
        a = math.fmod(year_x, 19)
        d = math.fmod(19 * a + m, 30)
        r = math.floor(d / 29) + (math.floor(d / 28) - math.floor(d / 29)) * math.floor(a / 11)
        og = 21 + d - r
        sz = 7 - math.fmod(year_x + math.floor(year_x / 4) + s, 7)
        oe = 7 - math.fmod(og - sz, 7)
        march_day = og + oe

        # conversion to day and month
        if march_day > 31:
            day = march_day - 31
            month = 4
        else:
            day = march_day
            month = 4
        d_eastersun = np.array([[day], [month]])

        return d_eastersun

    @staticmethod
    def func_xmasday(date_x):

        # determine christmas days 24.-26.12. and set them to true
        test_month = date_x.month == 12
        test_days = date_x.day == 24 | date_x.day == 25 | date_x.day == 26
        xmasday = int((test_month & test_days) is True)

        return xmasday
