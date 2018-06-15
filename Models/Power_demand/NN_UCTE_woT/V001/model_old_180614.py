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
        self.inputs['date'] = Input({'name': 'date'})

        # define outputs
        self.outputs['p_dem'] = Output({'name': 'power demand'})

        # define properties
        self.properties['offset'] = Property(10, float, {'name': 'demand offset'})

        # define persistent variables
        self.model_pars = None


    async def func_birth(self):
        dir = path.dirname(path.realpath(__file__))
        file = "model_parameter_LK_UCTE.txt"
        filepath = path.join(dir, file)
        try:
            with open(filepath, 'r') as f:
                f = open(filepath, 'r')
                json_str = f.read()
                data = json.loads(json_str)
        except Exception as e:
            print(e)
            data = None
        self.model_para = data


    async def func_peri(self, prep_to_peri=None):
        # get inputs
        dates = await self.get_input('date')
        print(dates)

        # date_list = ['01.01.2006 01:00', '01.01.2006 02:00', '01.01.2006 03:00', '01.01.2006 04:00']
        # date = datetime.strptime(date, '%d.%m.%Y %H:%M')
        # dates = [datetime.strptime(x, '%d.%m.%Y %H:%M') for x in date_list]

        # add country information to date
        # date_country = Model.prep_prop_array(dates)

        # date preparation
        NN_input = Model.prep_date(dates)

        # calculations
        demand = self.calc_demand(NN_input)

        # set output
        self.set_output("p_dem", demand)

    # @staticmethod
    # def prep_prop_array(date):
    #     # Length of date array
    #     l_date = len(date)
#
    #     # Create array with country indexes and its length
    #     country_index = np.linspace(1, 24, 24)
    #     l_country = len(country_index)
    #
    #     # Create array combining time and country array
    #     country_pred = np.tile(country_index, (1, l_date))
    #     date_pred = np.tile(date, (l_country, 1))
    #     date_pred = np.sort(date_pred, axis=None)
    #     date_pred = date_pred[np.newaxis]
    #
    #     prop_array = np.column_stack((date_pred, country_pred))
    #
    #     return prop_array
    #
    # @staticmethod
    # def prep_date(date_country):
    #
    #     # date_i = datetime.strptime(date_i, '%d.%m.%Y %H:%M')
    #     # date_local = date_UTC_to_local(date_i)
    #     date_UTC = date_country[:, 0]
    #     print('xyz')
    #     print(date_UTC)
    #     # date_UTC = date_UTC.tolist()
    #     date_local = date_UTC.astimezone(timezone('UTC'))
    #     weekend = date_local.isoweekday() == 6 | date_local.isoweekday() == 7
    #     if weekend == True:
    #         weekend = 1
    #     else:
    #         weekend = 0
    #     seconds = date_local.hour * 3600 + date_local.minute * 60
    #     holiday = Model.func_holiday(date_local)
    #     country = date_country[:, 1]
    #     nn_input = np.array([[date_local.year], [weekend], [seconds], [holiday], [country]])
    #
    #     return nn_input

    @staticmethod
    def prep_date(dates):

        #     l_date = len(date)
        #
        #     # Create array with country indexes and its length
        #     country_index = np.linspace(1, 24, 24)
        #     l_country = len(country_index)
        #
        #     # Create array combining time and country array
        #     country_pred = np.tile(country_index, (1, l_date))
        #     date_pred = np.tile(date, (l_country, 1))
        #     date_pred = np.sort(date_pred, axis=None)
        #     date_pred = date_pred[np.newaxis]
        #
        #     prop_array = np.column_stack((date_pred, country_pred))

        # date_i = datetime.strptime(date_i, '%d.%m.%Y %H:%M')
        # date_local = date_UTC_to_local(date_i)

        # Country
        country_index = np.linspace(1, 24, 24)
        l_country = len(country_index)

        # Date
        l_date = 1  #len(dates)
        date_UTC = dates
        date_local = date_UTC.astimezone(timezone('Europe/Brussels'))
        year = date_local.year
        weekend = int((date_local.isoweekday() == 6 | date_local.isoweekday() == 7) == True)
        seconds = date_UTC.hour * 3600 + date_UTC.minute * 60
        holiday = 1 #Model.func_holiday(date_local)
        # date_pred = np.array([[year], [weekend], [seconds], [holiday]])
        date_pred = np.array([[year, weekend, seconds, holiday]])
        date_pred = np.tile(date_pred, (l_country, 1))
        # date_pred = np.sort(date_pred, axis=0])
        sort_index = np.lexsort((date_pred[:, 3], date_pred[:, 2], date_pred[:, 1], date_pred[:, 0],))
        date_pred = date_pred[sort_index] # wenn mehrere Daten überprüfen !!!!!!!!!!!!!!

        country_pred = np.tile(country_index, (1, l_date))
        nn_input = np.append(date_pred, country_pred.transpose(), axis=1)

        return nn_input

    def calc_demand(self, nn_input):

        # calculation of demand per date and country
        demand_GW_i = self.func_NeuralNetwork(nn_input)

        # summarize per date over countries
        num_country = np.unique(nn_input[:, 4])
        demand_GW = np.add.reduceat(demand_GW_i, np.arange(0, len(demand_GW_i), len(num_country)))

        # convert GW to W
        demand = np.multiply(demand_GW, 10e9)

        return demand


    def func_NeuralNetwork(self, x1):
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
        # atilde = np.transpose(a.values)
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
        holidays = int((hday_1 | hday_2) == True)
        # holidays = hday_1 | hday_2
        # if holidays == True:
        #     holidays = 1
        # else:
        #     holidays = 0

        return holidays

    @staticmethod
    def func_easterday(date_x):
        year = date_x.year
        ret_eastersun = Model.func_eastersunday(year)
        d_eastersun = date(year, ret_eastersun[1], ret_eastersun[0])

        easter_start = d_eastersun - timedelta(days=2)
        easter_end = d_eastersun + timedelta(days=1)

        easterday = int(((easter_start <= date_x.date()) & (date_x.date() <= easter_end)) == True)
        # if easterday == True:
        #     easterday = 1
        # else:
        #     easterday = 0

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
        test_month = date_x.month == 12
        test_days = date_x.day == 24 | date_x.day == 25 | date_x.day == 26
        xmasday = test_month & test_days
        if xmasday == True:
            xmasday = 1
        else:
            xmasday = 0

        return xmasday


if __name__ == "__main__":
    model = Model(5,"hwfd")