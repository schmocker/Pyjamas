from core import Supermodel
from core.util import Input, Output, Property
import csv
from datetime import datetime
from Models._utils.time import datetime2utc_time, utc_time2datetime
import pandas as pd
import numpy as np
from pytz import timezone


# define the model class and inherit from class "Supermodel"
class Model(Supermodel):
    # model constructor
    def __init__(self, id, name: str):
        # instantiate supermodel
        super(Model, self).__init__(id, name)

        # define inputs
        self.inputs['mode'] = Input(name='modus', unit='-', info="modus (live or simulation")
        self.inputs['KW'] = Input(name='KW info', unit='-', info="KW information (id, lat, lon)")
        self.inputs['date'] = Input(name='Time vector', unit='s', info="Time in utc")

        # define outputs
        self.outputs['weather_data'] = Output(name='weather data of KWs')

        # define properties
        self.properties['T_offset'] = Property(0., float, name='temperature offset', unit='%', info="offset of temperature in %")
        self.properties['u_offset'] = Property(0., float, name='wind speed offset', unit='%', info="offset of wind speed in %")
        self.properties['P_offset'] = Property(0., float, name='radiation offset', unit='%', info="offset of radiation in %")
        self.properties['ref_year'] = Property(0., float, name='reference year', unit='%', info="reference year for modeled weather")

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
        mode = await self.get_input('mode')
        KW_data = await self.get_input('KW')
        dates = await self.get_input('date')

        # loop over KW's
        # - initialization
        out_ids = []
        out_T = []
        out_u = []
        out_P = []
        T_it = []
        u_it = []
        P_it = []
        len_id = KW_data["ID"].__len__()

        # - loop
        for it in range(0,len_id):

            id_it = KW_data["ID"][it]
            long = KW_data["Longitude"][it]
            lat = KW_data["Latitude"][it]

            # selection of weather model based on mode
            if mode == 'live':
                #w_data = 1
                w_data_it = [self.weather_API(self, long, lat, tt) for tt in dates]
                T_it = [item[0] for item in w_data_it]
                u_it = [item[1] for item in w_data_it]
                P_it = [item[2] for item in w_data_it]

            else:
                #w_data = 2
                w_data_it = [self.weather_historic(self, long, lat, tt, self.get_property('ref_year')) for tt in dates]
                T_it = [item[0] for item in w_data_it]
                u_it = [item[1] for item in w_data_it]
                P_it = [item[2] for item in w_data_it]

            # append data
            out_ids.append(id_it)
            out_T.append(T_it)
            out_u.append(u_it)
            out_P.append(P_it)

        # create dict
        weather_data = dict(zip(["ID", "Temperature", "Wind_speed", "Radiation"], [out_ids, out_T, out_u, out_P]))

        # set output
        self.set_output("weather_data", weather_data)

    def weather_API(self, long, lat, date):

        # API
        # data = http://my.meteoblue.com/packages/basic-1h?lat=47.5584&lon=7.57327&format=JSON&timeformat=timestamp_utc
        # no &tz= => data in local including daylight saving for europe
        # timeformat timestamp in utc

        # dummy
        T_it = 20
        u_it = 10
        P_it = 1000

        # offset
        # T_it = T_it*(1+self.get_property("T_offset")/100)
        # u_it = u_it * (1 + self.get_property("u_offset")/100)
        # P_it = P_it * (1 + self.get_property("P_offset")/100)

        w_data_it = [T_it, u_it, P_it]

        return w_data_it

    def weather_historic(self, long, lat, date, ref_year):

        # read weather data dependent on long and lat
        # and select data of reference year
        data_hist = self.historic_data_read(self, long, lat, ref_year)

        # read or interpolate weather data dependent on date
        d_weather = self.historic_interpolation(data_hist, date, ref_year)
        T_it = d_weather.iloc[0]['Temperature']
        u_it = d_weather.iloc[0]['Wind_speed']
        P_it = d_weather.iloc[0]['Radiation']

        # # trivial
        # T_it = 21
        # u_it = 11
        # P_it = 1001

        # offset
        T_it = T_it*(1+self.get_property("T_offset")/100)
        u_it = u_it * (1 + self.get_property("u_offset")/100)
        P_it = P_it * (1 + self.get_property("P_offset")/100)

        w_data_it = [T_it, u_it, P_it]

        return w_data_it

    def historic_data_read(self, long, lat, ref_year=2000):

        # select file to be read
        filename = self.historic_file_selection(long, lat)

        # read file
        with open(filename, 'r') as f:
            reader = csv.reader(f)
            next(reader)
            data = list(reader)
            #data = [r for r in reader]
            #print(data)

        # formatting
        data_t = list(map(list, zip(*data)))
        date = [datetime.strptime(x, '%Y-%m-%d %H:%M') for x in data_t[0]]
        date_s = np.asarray(date)
        date_s = date_s[np.newaxis, :]
        date_s = date_s.transpose()

        T_vec = np.asarray([float(x) for x in data_t[1]])
        u_vec = np.asarray([float(x) for x in data_t[2]])
        P_vec = np.asarray([float(x) for x in data_t[3]])

        T_vec = T_vec[np.newaxis, :]
        T_vec = T_vec.transpose()
        u_vec = u_vec[np.newaxis, :]
        u_vec = u_vec.transpose()
        P_vec = P_vec[np.newaxis, :]
        P_vec = P_vec.transpose()

        data_con = np.concatenate((date_s, T_vec, u_vec, P_vec), axis = 1)
        dataframe = pd.DataFrame(data_con, columns=['Date', 'Temperature', 'Wind_speed', 'Radiation'])
        dataframe.sort_values(by=['Date'])

        # select year
        year_vec = [x.year for x in dataframe['Date']]
        dataframe['Year'] = year_vec
        data_sel = dataframe.loc[dataframe['Year'] == ref_year]
        data_sel = data_sel.drop('Year', axis=1)

        return data_sel

    @staticmethod
    def historic_file_selection(long, lat):

        # Point 1: Europe - onshore
        filename = '../dummy_historic/Weather_2000.csv'

        return filename

    @staticmethod
    def historic_interpolation(data_hist, date, ref_year):

        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # Zeitzonen nach kontrollieren
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

        # check if date is within the list
        # - manipulate year of date to ref_year
        # ------------
        date = 1530801794.9515              # 05.07.2018 16:43 local
        #date = 1530802800.0                 # 05.07.2018 17:00 local
        date = int(date)
        # ------------
        date = utc_time2datetime(date)
        # date_UTC = date_UTC.replace(tzinfo=timezone('UTC'))
        # ? date_local = date_UTC.astimezone(timezone('Europe/Brussels'))
        date = date.replace(year=ref_year)
        date = date.replace(tzinfo=None)

        # - compare date with dates in data_hist
        date_in_list = data_hist.loc[data_hist['Date'] == date]
        if date_in_list.empty == False:
            weather_data = data_hist.loc[data_hist['Date'] == date]
            print('IN LIST')
        else:
            data_around = data_hist.iloc[(data_hist['Date'] - date).abs().argsort()[:2]]
            data_inter = data_around
            data_inter.loc[-1, 'Date'] = date
            data_inter = data_inter.sort_values('Date').reset_index(drop=True)
            data_inter['Temperature'] = pd.to_numeric(data_inter['Temperature'], errors='coerce')
            data_inter['Wind_speed'] = pd.to_numeric(data_inter['Wind_speed'], errors='coerce')
            data_inter['Radiation'] = pd.to_numeric(data_inter['Radiation'], errors='coerce')
            data_inter = data_inter.interpolate(method='linear')    #(method='time')
            weather_data = data_inter.iloc[[1]]
            print('NOT IN LIST -> INTERPOLATION')

        return weather_data
