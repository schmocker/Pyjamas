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


# define the model class and inherit from class "Supermodel"
class Model(Supermodel):
    # model constructor
    def __init__(self, id, name: str):
        # instantiate supermodel
        super(Model, self).__init__(id, name)

        # define inputs
        self.inputs['mode'] = Input(name='modus', unit='-', info="modus (live or simulation)")
        self.inputs['KW'] = Input(name='KW info', unit='-', info="KW information (id, lat, lon)")
        self.inputs['date'] = Input(name='Time vector', unit='s', info="Time in utc")

        # define outputs
        self.outputs['weather_data'] = Output(name='weather data of KWs', unit='date, °C, m/s, ???', info='????')

        # define properties
        self.properties['T_offset'] = Property(default=0., data_type=float, name='temperature offset', unit='%', info="offset of temperature in %")
        self.properties['u_offset'] = Property(default=0., data_type=float, name='wind speed offset', unit='%', info="offset of wind speed in %")
        self.properties['P_offset'] = Property(default=0., data_type=float, name='radiation offset', unit='%', info="offset of radiation in %")
        self.properties['ref_year'] = Property(default=2000, data_type=int, name='reference year', unit='-', info="reference year for modeled weather")

        # define persistent variables
        self.data_hist = None
        self.data_hist_year = None

    async def func_birth(self):
        # read historic weather data
        self.data_hist = self.historic_data_read()

        await self.func_amend(['ref_year'])

    async def func_amend(self, keys=[]):

        if 'ref_year' in keys:
            ref_year = self.get_property('ref_year')
            self.data_hist_year = self.historic_select_year(self.data_hist, ref_year)

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
                ref_year = self.get_property('ref_year')
                w_data_it = [self.weather_historic(long, lat, tt, ref_year) for tt in dates]
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
        # data_hist = self.historic_data_read(long, lat, ref_year)
        data_hist = self.data_hist_self

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

    @staticmethod
    def historic_data_read():

        filename = 'Models/Weather/Preparation_historic_weather/V001/dict_hist.json'
        with open(filename, 'r') as f:
            data_hist = json.load(f)
        return data_hist

    @staticmethod
    def historic_select_year(data_hist, ref_year):









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
        filename = 'Models/Weather/Weather_1/dummy_historic/Weather_2000.csv'

        return filename

    def historic_interpolation(self, data_hist, date, ref_year):

        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # Zeitzonen nach kontrollieren
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

        # check if date is within the list
        # - manipulate year of date to ref_year
        # ------------
        date = 1530801794.9515              # 05.07.2018 16:43 local
        date = 1530802800.0                 # 05.07.2018 17:00 local
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
            print('NOT IN LIST -> INTERPOLATION')
            list_lat = np.repeat(1,1)
            list_long =
            weather_data = self.interpol_3d(self, list(data_hist.Date), db_lat, db_long, db_values, interp_lat, interp_long, interp_time)

        return weather_data

    # 3D Interpolation based on 3D Interpolation European_power_plant
    def interpol_3d(self, db_time, db_lat, db_long, db_values, interp_lat, interp_long, interp_time):
        """
        This function interpolates in a grid of points (db_lat,db_long,db_time) with assigned values (db_values).
        It interpolates for points given by (interp_lat, interp_long, interp_time) and outputs their corresponding value.

        Values inside the grid are interpolated linearly and values outside of the grid are interpolated to the
        nearest point of the grid.

        ATTENTION: If there are less than 4 points in db_... no grid can be formed and everything will be "interpolated"
                   to nearest.
                   Also, it is not allowed to have all points forming a plane, they must span a 3dimensional space

        |  "db_" inputs are things as location, temperature, time
        |  "interp_" inputs denote the points to interpolate

        INPUTS:
            |  db_lat: Latitude, list of [float]; nx1
            |  db_long: Longitude, list of [float]; nx1
            |  db_time: Time, list of [datetime]; nx1
            |  db_values: list of [float]; nx1
            |  interp_lat: Latitude, list of [float]; jx1
            |  interp_long: Longitude, list of [float]; jx1
            |  interp_time: Time, list of [datetime]; jx1

        OUTPUTS:
            interp_values: ndarray of [float]; jx1
        """
        db_lat = np.asarray(db_lat)
        db_long = np.asarray(db_long)
        db_time = np.asarray(db_time)
        db_values = np.asarray(db_values)
        interp_lat = np.asarray(interp_lat)
        interp_long = np.asarray(interp_long)
        interp_time = np.asarray(interp_time)

        # change time values from datetime to float
        db_timestamp = np.asarray([datetime.datetime.timestamp(i) for i in db_time])
        interp_timestamp = np.asarray([datetime.datetime.timestamp(i) for i in interp_time])
        # arrange inputs for griddata
        xi = np.vstack((interp_lat, interp_long, interp_timestamp))
        gridpoints = np.vstack((db_lat, db_long, db_timestamp))

        # interpolate
        interp_nearest = griddata(gridpoints.T, db_values.T, xi.T, method='nearest')
        if db_values.size < 4:
            interp_values = interp_nearest
        else:
            interp_linear = griddata(gridpoints.T, db_values.T, xi.T, method='linear')
            # replace Nan in linear with nearest (out of range values)
            interp_values = np.where(np.isnan(interp_linear), interp_nearest, interp_linear)

        return interp_values
