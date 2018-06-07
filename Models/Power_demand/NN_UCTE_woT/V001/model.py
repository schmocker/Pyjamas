from core import Supermodel
from core.util import Input, Output, Property

from flask import Markup
import markdown2
import os
from pathlib import Path

import numpy as np
import json
from datetime import datetime, timedelta, date
import math

# define the model class and inherit from class "Supermodel"
class Model(Supermodel):
    # model constructor
    def __init__(self, id, name: str):
        # instantiate supermodel
        super(Model, self).__init__(id, name)

        # define inputs
        self.inputs['date'] = Input({'name': 'date'})
        #self.inputs['dir'] = Input({'name': 'wind direction'})

        # define outputs
        self.outputs['p_dem'] = Output({'name': 'power demand'})

        # define properties
        self.properties['h_hub'] = Property(10, {'name': 'hub height'})


        # define persistent variables
        #self.pers_variable_0 = 5

    async def func_birth(self):
        pass

    async def func_prep(self):
        # calculate something
        prep_result = 3 * 5
        # pass values to peri function
        return prep_result

    async def func_peri(self, prep_to_peri=None):
        prep_result = prep_to_peri
        # get inputs
        in1 = await self.get_input('v')
        in2 = await self.get_input('dir')

        # calculate something
        # One can declare custom functions (eg: see end of file)
        # If you declare them "async" you will have to "await" them (like "extremely_complex_calculation")
        # Else one could declare "normal" (blocking) functions as well (like "complex_calculation")
        out1 = prep_result * self.complex_calculation(in1)
        out2 = await self.extremely_complex_calculation(in1, in2)

        # set output
        self.set_output("p_el", out1)
        self.set_output("f_rot", out2)

        # pass values to post function
        outputs = {'out1': out1, 'out2': out2}
        return outputs

    async def func_post(self, peri_to_post=None):
        outputs = peri_to_post
        # do something with the values (eg: overwrite persistent variable)
        self.pers_variable_0 = outputs['out1']

    async def func_death(self):
        print("I am dying! Bye bye!")

    # define additional methods (normal)
    def complex_calculation(self, speed):
        speed_cut = speed / self.pers_variable_0
        return speed_cut

    def prep_date(self, date_i, country_i):

        date_i = '01.01.2006 01:00'

        date_i = datetime.strptime(date_i,'%d.%m.%Y %H:%M')
        weekend = date_i.isoweekday()==6 | date_i.isoweekday()==7
        if weekend==True:
            weekend = 1
        else:
            weekend = 0
        seconds = date_i.hour*3600+date_i.minute*60
        holiday = func_holiday(date_i)
        country = 1
        NN_input = np.array([[date_i.year], [weekend], [seconds], [holiday], [country]])

        NN_output = func_NeuralNetwork(NN_input)

        return NN_output

    def func_NeuralNetwork(self, data):

        # read parameters
        file = open("model_parameter_LK_UCTE.txt", "r")
        json_str = file.read()
        model_para = json.loads(json_str)

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
        xp1 = mapminmax_apply(x1, x1_step1)

        # Layer 1
        a1 = tansig_apply(np.tile(b1, (1, Q)) + np.matmul(IW1_1, xp1))

        # Layer 2
        a2 = np.tile(b2, (1, Q)) + np.matmul(LW2_1, a1)

        # Output 1
        y1 = mapminmax_reverse(a2, y1_step1)

        return y1


    def mapminmax_apply(self, a, x1_step1):

        atilde = np.transpose(a.values)
        y = np.add(atilde, -np.array(x1_step1['xoffset']))
        y = y * np.array(x1_step1['gain'])
        y = y + np.array(x1_step1['ymin'])
        y = np.transpose(y)

        return y


    def tansig_apply(self, n):

        a = 2 / (1 + np.exp(-2 * n)) - 1

        return a


    def mapminmax_reverse(self, a, y1_step1):

        x = a - np.array(y1_step1['ymin'])
        x = x / np.array(y1_step1['gain'])
        x = x + np.array(y1_step1['xoffset'])

        return x


    def func_holiday(self, date_x):
        # eastern
        hday_1 = func_easterday(date_x)

        # christmas
        hday_2 = func_xmasday(date_x)

        # holidays
        holidays = hday_1 | hday_2
        if holidays == True:
            holidays = 1
        else:
            holidays = 0

        return holidays

    def func_easterday(self, date_x):
        ret_eastersun = func_eastersunday(date_x.year)
        d_eastersun = date(date_x.year,ret_eastersun[1],ret_eastersun[0])

        easter_start = d_eastersun-timedelta(days=2)
        easter_end = d_eastersun+timedelta(days=1)

        easterday = easter_start<=date_x.date() & date_x.date()<=easter_end
        if easterday == True:
            easterday = 1
        else:
            easterday = 0

        return easterday

    def func_eastersunday(self, year_x):

        # easter formula based on Heiner Lichtenberg
        k = math.floor(year_x/100)
        m = 15+math.floor((3*k+3)/4)-math.floor((8*k+13)/25)
        s = 2-math.floor((3*k+3)/4)
        a = math.fmod(year_x, 19)
        d = math.fmod(19*a+m, 30)
        r = math.floor(d/29)+(math.floor(d/28)-math.floor(d/29))*math.floor(a/11)
        og = 21+d-r
        sz = 7-math.fmod(year_x+math.floor(year_x/4)+s, 7)
        oe = 7-math.fmod(og-sz, 7)
        march_day = og+oe

        # conversion to day and month
        if march_day > 31:
            day = march_day-31
            month = 4
        else:
            day = march_day
            month = 4
        d_eastersun = np.array([[day], [month]])

        return d_eastersun

    def func_xmasday(self, date_x):
        test_month = date_x.month == 12
        test_days = date_x.day == 24 | date_x.day == 25 | date_x.day == 26
        xmasday = test_month & test_days
        if xmasday == True:
            xmasday = 1
        else:
            xmasday = 0

        return xmasday


    # define additional methods (async)
    async def extremely_complex_calculation(self, speed, time):
        distance = speed * time / self.pers_variable_0
        return distance




    ######### TODO:
    @property
    def description(self):
        script_dir = os.path.dirname(__file__)
        abs_file_path = Path(os.path.join(script_dir, 'README.md'))
        if abs_file_path.exists():
            txt = open(abs_file_path, 'r', encoding="utf8").read()
            mkdwn = markdown2.markdown(txt, extras=['extra', 'fenced-code-blocks'])
            return Markup(mkdwn)
        else:
            return ""

