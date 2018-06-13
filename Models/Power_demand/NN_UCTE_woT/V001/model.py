from core import Supermodel
from core.util import Input, Output, Property
import numpy as np
from pytz import timezone
import math
from datetime import date, timedelta
import aiofiles
import json


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

        filepath = "model_parameter_LK_UCTE.txt"

        # f = open(filepath, 'r')
        print(True)
        json_str = '{"x1_step1":{"xoffset":[1,0,0,0,1],"gain":[0.00547945205479452,2,2.33918128654971E-5,2,0.0869565217391304],"ymin":-1},"b1":[32.918315121501429,-21.735948473330193,3.1729627613802629,-3.9287734621542638,3.4622647221199583,3.6401910847154282,-3.1212244913595057,-2.5212911118095103,-3.3974701542685262,5.0816799097450653],"IW1_1":[[0.0072003447507769354,-0.032430419091604226,-0.50334797970776979,-0.050033483520066209,69.009733524516],[-0.0071653263453592469,0.035040771506084596,0.5011294099734831,0.050146913254439471,-45.574985389310569],[-0.42272190501246892,-0.017703420001601324,0.026316504992700079,3.6705538646648113,0.31572359379406317],[0.0034501986356111616,10.730527287715704,0.053377206768064241,3.9476244202444328,16.318938229529589],[0.66169499800650455,0.017268289681208977,-0.017333735580827542,2.9374454619709884,-0.33535218885328727],[-0.017279290324363164,-0.056661206827611423,0.067103819927766734,-5.5596461123786405,0.75576156036352149],[0.022056492827728438,5.3155746235393009,-0.037930246656677616,3.9395708832705747,-8.181108826615711],[-0.040423471810349686,0.77478324381163377,-9.81875250576762,0.25291281702638169,0.45249631041588528],[0.027629608606716666,-5.13730926566445,-0.070541152668442839,3.4483901716044638,-7.9178360826084235],[0.0016519017420891615,11.639508605844712,-0.074569298882450341,-3.4956730553898772,-17.769050522412734]],"b2":-1.0072090631661088,"LW2_1":[-42.22319652976293,-42.141382584102395,-1.8703506501998177,-1.6217352553297364,-1.2474966867062978,-3.5795935161822436,-1.8123706895667642,-0.0325746319910914,-1.8016519447673536,1.6015557434240193],"y1_step1":{"ymin":-1,"gain":1.95895979235026E-5,"xoffset":3}}'
        print(json_str)
        print(True)
        data = json.loads(json_str)
        print(data)
        print(True)


        self.model_para = data


    async def func_peri(self, prep_to_peri=None):
        # get inputs
        dates = await self.get_input('date')
        print(dates)

        # date_list = ['01.01.2006 01:00', '01.01.2006 02:00', '01.01.2006 03:00', '01.01.2006 04:00']
        # date = datetime.strptime(date, '%d.%m.%Y %H:%M')
        # dates = [datetime.strptime(x, '%d.%m.%Y %H:%M') for x in date_list]

        # add country information to date
        date_country = Model.prep_prop_array(dates)

        # date preparation
        NN_input = Model.prep_date(date_country)

        # calculations
        demand = self.calc_demand(NN_input)

        # set output
        self.set_output("p_dem", demand)

    @staticmethod
    def prep_prop_array(date):
        # Length of date array
        l_date = len(date)

        # Create array with country indexes and its length
        country_index = np.linspace(1, 24, 24)
        l_country = len(country_index)

        # Create array combining time and country array
        country_pred = np.tile(country_index, (1, l_date))
        date_pred = np.tile(date, (l_country, 1))
        date_pred = np.sort(date_pred, axis=None)
        date_pred = date_pred[np.newaxis]

        prop_array = np.column_stack((date_pred, country_pred))

        return prop_array

    @staticmethod
    def prep_date(date_country):

        # date_i = datetime.strptime(date_i, '%d.%m.%Y %H:%M')
        # date_local = date_UTC_to_local(date_i)
        date_UTC = date_country[:, 0]
        date_local = date_UTC.astimezone(timezone('UTC'))
        weekend = date_local.isoweekday() == 6 | date_local.isoweekday() == 7
        if weekend == True:
            weekend = 1
        else:
            weekend = 0
        seconds = date_local.hour * 3600 + date_local.minute * 60
        holiday = Model.func_holiday(date_local)
        country = date_country[:, 1]
        nn_input = np.array([[date_local.year], [weekend], [seconds], [holiday], [country]])

        return nn_input



    def calc_demand(self, nn_input):

        # calculation of demand per date and country
        demand_GW_i = self.func_NeuralNetwork(nn_input)

        # summarize per date over countries
        num_country = np.unique(nn_input[:, 4])
        demand_GW = np.add.reduceat(demand_GW_i, np.arange(0, len(demand_GW_i), num_country))

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
        atilde = np.transpose(a.values)
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
        holidays = hday_1 | hday_2
        if holidays == True:
            holidays = 1
        else:
            holidays = 0

        return holidays

    @staticmethod
    def func_easterday(date_x):
        ret_eastersun = Model.func_eastersunday(date_x.year)
        d_eastersun = date(date_x.year, ret_eastersun[1], ret_eastersun[0])

        easter_start = d_eastersun - timedelta(days=2)
        easter_end = d_eastersun + timedelta(days=1)

        easterday = easter_start <= date_x.date() & date_x.date() <= easter_end
        if easterday == True:
            easterday = 1
        else:
            easterday = 0

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
