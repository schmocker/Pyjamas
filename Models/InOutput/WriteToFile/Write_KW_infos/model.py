from pyjamas_core.util import Input, Output, Property
from pyjamas_core.supermodel import Supermodel
from datetime import datetime, timedelta
from Models._utils.time import datetime2utc_time, utc_time2datetime
import numpy as np
from pytz import timezone
import json
from scipy.interpolate import griddata
import pandas as pd
import requests
import os
import itertools
import math

# define the model class and inherit from class "Supermodel"
class Model(Supermodel):
    # model constructor
    def __init__(self, id, name: str):
        # instantiate supermodel
        super(Model, self).__init__(id, name)

        # define inputs
        self.inputs['KW_data'] = Input(name='KW data', unit='-', info="KW data")

        # define outputs
        #self.outputs['KW_weather'] = Output(name='Weather data of KWs', unit='dict{id, windspeed, radiation, windmesshoehe}', info='weather data of KWs')

        # define properties
        self.properties['date_start'] = Property('Simulation Start (UTC)', default="2018-01-01 00:00", data_type=str, unit='YYYY-MM-DD hh:mm')
        self.properties['date_delta_time'] = Property('Simulation time increase', default=1, data_type=float, unit='s', info='Amount of seconds the simulation time increases with each iteration')
        self.properties['date_end'] = Property('Simulation Stop (UTC)', default="2999-01-01 00:00", data_type=str, unit='YYYY-MM-DD hh:mm')

        # Define persistent variables
        self.date_start = None
        self.date_delta = None
        self.date_end = None

    async def func_birth(self):
        pass

    async def func_amend(self, keys=[]):
        # start date
        if 'date_start' in keys:
            self.date_start = self.get_property('date_start')

        # date delta time
        if 'date_delta_time' in keys:
            self.date_delta = self.get_property('date_delta_time')

        # end date
        if 'date_end' in keys:
            self.date_end = self.get_property('date_end')

    async def func_peri(self, prep_to_peri=None):

        # inputs
        KW_data = await self.get_input('KW_data')

        # file indicator
        # - create filename
        s_general = "Data_KW"
        s_start = self.date_start[0:10]
        s_delta = str(int(self.date_delta))
        s_end = self.date_end[0:10]
        file_format = '.txt'
        s_file = s_general + "_" + s_start + "_" + s_delta + "_" + s_end + file_format

        # - search file with this time
        path = os.path.abspath(__file__)
        dir_path = os.path.dirname(path)
        file_path = dir_path + "/Data_Files"
        files_in_confidential = os.listdir(file_path)
        files_match = [s for s in files_in_confidential if s_file in s]

        # if no file math - create new file
        path = os.path.abspath(__file__)
        dir_path = os.path.dirname(path)
        file_str = ''.join(s_file)
        filename = os.path.join(dir_path, 'Data_Files', file_str)
        if files_match == []:
            open(filename, 'w').close()
            # write head line
            with open(filename, 'a') as f:
                write_s = "KW_id"
                write_s = write_s + "\t" + "KW_Bezeichnung"
                write_s = write_s + "\t" + "P_installed"
                write_s = write_s + "\t" + "Bez_Kraftwerkstyp"
                #write_s = write_s + " \t Load"
                #write_s = write_s + " \t Grenzkosten"
                #write_s = write_s + " \t Distanzkosten"
                #write_s = write_s + " \t Totalkosten"
                write_s = write_s + "\n"
                f.write(write_s)
                # write data
                for ni in range(0, KW_data['id'].__len__()):
                    write_s = str(KW_data['id'][ni]) + "\t" + \
                              str(KW_data['kw_bezeichnung'][ni]) + "\t" + \
                              str(KW_data['p_inst'][ni]) + "\t" + \
                              str(KW_data['bez_kraftwerkstyp'][ni]) + "\n"
                    f.write(write_s)


if __name__ == "__main__":

    props = {}
    inputs = {}
    outputs = Model.test(inputs, props)
