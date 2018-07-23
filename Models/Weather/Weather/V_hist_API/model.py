from core import Supermodel
from core.util import Input, Output, Property
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

# define the model class and inherit from class "Supermodel"
class Model(Supermodel):
    # model constructor
    def __init__(self, id, name: str):
        # instantiate supermodel
        super(Model, self).__init__(id, name)

        # define inputs
        self.inputs['mode'] = Input(name='modus', unit='-', info="modus (is live of not")
        self.inputs['KW'] = Input(name='KW info', unit='-', info="KW informations (u.a. id, lat, lon)")
        self.inputs['date'] = Input(name='Futures', unit='s', info="Time vector of futures in utc timestamp [s]")

        # define outputs
        self.outputs['KW_weather'] = Output(name='Weather data of KWs', unit='dict{id, windspeed, radiation, windmesshoehe}', info='weather data of KWs')
        self.outputs['Futures_weather'] = Output(name='Weather data', unit='s, °C, m/s, W/m^2', info='weather data for 25 points (time, temperature, wind speed, radiation)')

        # define properties
        self.properties['T_offset'] = Property(default=0., data_type=float, name='temperature offset', unit='%', info="offset of temperature in %", example='100: doubles the value')
        self.properties['u_offset'] = Property(default=0., data_type=float, name='wind speed offset', unit='%', info="offset of wind speed in %", example='100: doubles the value')
        self.properties['P_offset'] = Property(default=0., data_type=float, name='radiation offset', unit='%', info="offset of radiation in %", example='100: doubles the value')
        self.properties['ref_year'] = Property(default=2007, data_type=int, name='reference year', unit='-', info="reference year for modeled weather (2007-2016; provided data for 2006-2017)",
                                               example='2007')

        # define persistent variables
        self.data_hist = None
        self.ref_year = None

    async def func_birth(self):
        # read historic data from file
        self.data_hist = self.historic_data_read()

    async def func_amend(self, keys=[]):

        # reference year
        if 'ref_year' in keys:
            self.ref_year = self.get_property('ref_year')

    async def func_peri(self, prep_to_peri=None):

        # inputs
        islive = await self.get_input('mode')
        KW_data_orig = await self.get_input('KW')
        KW_data = {k: KW_data_orig[k] for k in ('id', 'bez_kraftwerkstyp', 'lat', 'long')}
        futures = await self.get_input('date')

        # weather data
        # - test first future is equal or later than now, and less than 7 days
        date_now = datetime.now()
        date_now_s = date_now.timestamp()
        dt_limit = 7*24*60*60
        if (futures[0] >= date_now_s) & (futures[len(futures)-1] < (date_now_s + dt_limit)):
            future_indicator = True
        else:
            future_indicator = False

        # dependent on future, select weather source (API or historic)
        if future_indicator:
            # current weather forecast by API
            weather_data = self.prepare_API_weather()
            #print('API')
        else:
            # historic weather data from a reference year
            weather_data = self.prepare_historic_weather(futures)
            #print('hist')

        # KW weather
        # interpolate weather data in times and locations for the different KW's
        KW_weather_data = self.KW_weather_data(KW_data, weather_data, futures)

        # futures weather
        # editing weather data for further use (e.g. power demand model)
        futures_weather_data = self.future_weather_data(weather_data)

        # set output
        self.set_output("KW_weather", KW_weather_data)
        self.set_output("Futures_weather", futures_weather_data)

    @staticmethod
    def historic_data_read():

        # read historic weather data
        path = os.path.abspath(__file__)
        dir_path = os.path.dirname(path)
        filename = os.path.join(dir_path, 'confidential', 'dict_hist')
        with open(filename, 'r') as f:
            data_hist = json.load(f)
        return data_hist

    def prepare_API_weather(self):

        # test if new data is available
        # - current time
        date_now = datetime.utcnow()
        # - shift 12 h back (considering running time of forecast)
        date_forecast = date_now - timedelta(hours=12)
        if date_forecast.hour >= 12:
            date_comp = date_forecast.strftime('%Y_%m_%d_12_00')
        else:
            date_comp = date_forecast.strftime('%Y_%m_%d_00_00')
        # - search file with this time
        path = os.path.abspath(__file__)
        dir_path = os.path.dirname(path)
        file_path = dir_path + "/confidential"
        files_in_confidential = os.listdir(file_path)
        files_match = [s for s in files_in_confidential if date_comp in s]

        # if no file math - get new data
        if files_match == []:
            data_API = self.load_API_weather(date_comp)
        # else load previous data
        else:
            path = os.path.abspath(__file__)
            dir_path = os.path.dirname(path)
            file_str = ''.join(files_match)
            filename = os.path.join(dir_path, 'confidential', file_str)
            with open(filename, 'r') as f:
                data_API = json.load(f)

        # create database (formatting)
        data_base = self.create_database_API(data_API)

        return data_base

    @staticmethod
    def load_API_weather(date_comp):

        # read API_keys
        path = os.path.abspath(__file__)
        dir_path = os.path.dirname(path)
        filename = os.path.join(dir_path, 'confidential', 'API_Key')
        with open(filename, "r") as f:
            API_key = f.read().splitlines()

        data_API_all = []
        for url_api in API_key:
            data_API_i = requests.get(url_api).json()
            data_API_all.append(data_API_i)

        filename_w = os.path.join(dir_path, 'confidential', 'dict_API_')
        filename_w = filename_w + date_comp
        with open(filename_w, 'w') as fp:
            json.dump(data_API_all, fp)

        return data_API_all

    def create_database_API(self, data_API):

        # number of locations
        num_points = len(data_API)

        # initialize data vectors
        lat_vec = []
        lon_vec = []
        time_vec = []
        temp_vec = []
        wind_vec = []
        rad_vec = []

        # for all locations, fill vectors
        for it in range(0, num_points):
            len_time = len(data_API[it]['data_1h']['time'])
            lat_vec.append(np.repeat(data_API[it]['metadata']['latitude'], len_time).tolist())
            lon_vec.append(np.repeat(data_API[it]['metadata']['longitude'], len_time).tolist())
            time_vec.append(np.array(data_API[it]['data_1h']['time']).tolist())
            temp_vec.append(data_API[it]['data_1h']['temperature'])
            wind_vec.append(data_API[it]['data_1h']['windspeed'])
            rad_vec.append(data_API[it]['data_1h']['ghi_instant'])

        # flatten list
        lat_vec = list(itertools.chain(*lat_vec))
        lon_vec = list(itertools.chain(*lon_vec))
        time_vec = list(itertools.chain(*time_vec))
        temp_vec = list(itertools.chain(*temp_vec))
        wind_vec = list(itertools.chain(*wind_vec))
        rad_vec = list(itertools.chain(*rad_vec))

        # chance format to arrays and transpose
        lat_vec = np.array(lat_vec)
        lon_vec = np.array(lon_vec)
        # - change time format from string to seconds
        time_vec = [datetime.strptime(xi, '%Y-%m-%d %H:%M') for xi in time_vec]
        time_vec = [datetime2utc_time(xi) for xi in time_vec]
        time_vec = np.array(time_vec)
        temp_vec = np.array(temp_vec)
        wind_vec = np.array(wind_vec)
        rad_vec = np.array(rad_vec)

        lat_vec = lat_vec[np.newaxis, :].transpose()
        lon_vec = lon_vec[np.newaxis, :].transpose()
        time_vec = time_vec[np.newaxis, :].transpose()
        temp_vec = temp_vec[np.newaxis, :].transpose()
        wind_vec = wind_vec[np.newaxis, :].transpose()
        rad_vec = rad_vec[np.newaxis, :].transpose()

        # offset for temperature, wind speed and radiation
        temp_vec = np.multiply(temp_vec, (1 + self.get_property('T_offset') / 100))
        wind_vec = np.multiply(wind_vec, (1 + self.get_property('u_offset') / 100))
        rad_vec = np.multiply(rad_vec, (1 + self.get_property('P_offset') / 100))

        # create matrix
        data_base = np.concatenate((lat_vec, lon_vec, time_vec, temp_vec, wind_vec, rad_vec), axis=1)

        return data_base

    def prepare_historic_weather(self, futures):

        # leap year
        # - if future and reference year do not correspond in leap year or not, adjust reference year
        first_future_y = utc_time2datetime(futures[0])
        year_first_future = first_future_y.year
        leap_futures = self.det_leap_year(year_first_future)
        leap_refyear = self.det_leap_year(self.ref_year)
        leapyear_inref = np.array([2008, 2012, 2016])
        if leap_futures != leap_refyear:
            if leap_futures:
                # adjust to nearest leap year
                idx = (np.abs(leapyear_inref-self.ref_year)).argmin()
                self.ref_year = leapyear_inref[idx]
            else:
                # adjust to year before
                self.ref_year = self.ref_year - 1

        # define range (one day before till one day after futures)
        first_future = futures[0]
        last_future = futures[len(futures)-1]
        first_future_date = utc_time2datetime(first_future)
        first_hist_date = first_future_date.replace(year=self.ref_year)
        first_hist = datetime2utc_time(first_hist_date)
        delta_shift = first_future-first_hist
        before_first_hist = first_hist - 24*60*60
        after_last_hist = last_future - delta_shift + 24*60*60

        # filter data to one before and one after
        time_vec = np.array(self.data_hist["times"])
        # - determine indexes
        index_first = (np.abs(time_vec-before_first_hist).argmin())
        index_last = (np.abs(time_vec-after_last_hist).argmin())

        time_filter = time_vec[index_first:index_last]
        # - shift historic time to future
        time_filter = time_filter + delta_shift

        temp_filter = []
        wind_filter = []
        rad_filter = []
        for ni in range(0, len(self.data_hist["ids"])):

            temp_filter.append(self.data_hist["temperature"]["values"][ni][index_first:index_last])
            wind_filter.append(self.data_hist["windspeed"]["values"][ni][index_first:index_last])
            rad_filter.append(self.data_hist["radiation"]["values"][ni][index_first:index_last])

        # create data base
        # - lengths
        num_points = len(self.data_hist["lat"])
        num_times = len(time_filter)

        # - initialize vectors
        lat_vec = []
        lon_vec = []
        temp_vec = []
        wind_vec = []
        rad_vec = []
        # - fill
        time_vec = np.tile(np.array(time_filter), num_points)
        for it in range(0, num_points):
            lat_vec.append(np.repeat(self.data_hist["lat"][it], num_times))
            lon_vec.append(np.repeat(self.data_hist["lon"][it], num_times))
            temp_vec.append(np.array(self.data_hist["temperature"]["values"][it][index_first:index_last]))
            wind_vec.append(np.array(self.data_hist["windspeed"]["values"][it][index_first:index_last]))
            rad_vec.append(np.array(self.data_hist["radiation"]["values"][it][index_first:index_last]))
        # - change format to np.array and transposing
        lat_vec = np.array(lat_vec).ravel()
        lon_vec = np.array(lon_vec).ravel()
        time_vec = np.array(time_vec).ravel()
        temp_vec = np.array(temp_vec).ravel()
        wind_vec = np.array(wind_vec).ravel()
        rad_vec = np.array(rad_vec).ravel()

        lat_vec = lat_vec[np.newaxis, :].transpose()
        lon_vec = lon_vec[np.newaxis, :].transpose()
        time_vec = time_vec[np.newaxis, :].transpose()
        temp_vec = temp_vec[np.newaxis, :].transpose()
        wind_vec = wind_vec[np.newaxis, :].transpose()
        rad_vec = rad_vec[np.newaxis, :].transpose()

        # offset for temperature, wind speed and radiation
        temp_vec = np.multiply(temp_vec, (1 + self.get_property('T_offset') / 100))
        wind_vec = np.multiply(wind_vec, (1 + self.get_property('u_offset') / 100))
        rad_vec = np.multiply(rad_vec, (1 + self.get_property('P_offset') / 100))

        # create data base
        data_base = np.concatenate((lat_vec, lon_vec, time_vec, temp_vec, wind_vec, rad_vec), axis=1)

        return data_base

    @staticmethod
    def det_leap_year(year):

        if year % 4 == 0:
            if year % 100 == 0:
                if year % 400 == 0:
                    leap = True
                else:
                    leap = False
            else:
                leap = True
        else:
            leap = True

        return leap

    def KW_weather_data(self, KW_data, weather_data, futures):

        # naming of columns of KW_data (ones to be extracted)
        KW_data_columns = ['id', 'bez_kraftwerkstyp', 'lat', 'long']

        # create data frame from KW_data dict
        KW_data_df = pd.DataFrame(KW_data)

        # select only photovoltaic and wind turbine data
        PV_data = KW_data_df.loc[KW_data_df[KW_data_columns[1]] == 'Photovoltaik']
        WT_data = KW_data_df.loc[KW_data_df[KW_data_columns[1]] == 'Windturbine']

        # create data frame from weather data base (array)
        weather_df = pd.DataFrame(data=weather_data, columns=['lat', 'lon', 'time', 'temperature', 'windspeed', 'radiation'])

        # select relevant columns for photovoltaics and wind turbines
        weather_PV = weather_df[['lat', 'lon', 'time', 'radiation']]
        weather_WT = weather_df[['lat', 'lon', 'time', 'windspeed']]

        # 2D interpolation over KW locations (latitude/longitude)
        time_vec = weather_df['time'].unique()
        PV_weather_2D = pd.DataFrame()
        WT_weather_2D = pd.DataFrame()
        PV_weather_2D_ft_df = PV_data.copy()
        PV_weather_2D_ft_df['radiation'] = [None] * PV_weather_2D_ft_df['id'].__len__()
        PV_weather_2D_ft_df['time'] = [None] * PV_weather_2D_ft_df['id'].__len__()
        WT_weather_2D_ft_df = WT_data.copy()
        WT_weather_2D_ft_df['windspeed'] = [None] * WT_weather_2D_ft_df['id'].__len__()
        WT_weather_2D_ft_df['time'] = [None] * WT_weather_2D_ft_df['id'].__len__()
        for tt in time_vec:

            weather_PV_tt = weather_PV.loc[weather_PV['time'] == tt]
            weather_WT_tt = weather_WT.loc[weather_WT['time'] == tt]

            PV_weather_2D_ft = self.interpol_2d(list(weather_PV_tt['lat']), list(weather_PV_tt['lon']), list(weather_PV_tt['radiation']),
                                                list(PV_data[KW_data_columns[2]]), list(PV_data[KW_data_columns[3]]))
            WT_weather_2D_ft = self.interpol_2d(list(weather_WT_tt['lat']), list(weather_WT_tt['lon']), list(weather_WT_tt['windspeed']),
                                                list(WT_data[KW_data_columns[2]]), list(WT_data[KW_data_columns[3]]))

            PV_weather_2D_ft_df['radiation'] = PV_weather_2D_ft.tolist()
            PV_weather_2D_ft_df['time'] = [tt] * PV_weather_2D_ft_df['id'].__len__()
            WT_weather_2D_ft_df['windspeed'] = WT_weather_2D_ft.tolist()
            WT_weather_2D_ft_df['time'] = [tt] * WT_weather_2D_ft_df['id'].__len__()

            PV_weather_2D = PV_weather_2D.append(PV_weather_2D_ft_df)
            WT_weather_2D = WT_weather_2D.append(WT_weather_2D_ft_df)

        # 1D interpolation over time (fixed locations)
        # - photovoltaics
        id_vec = PV_weather_2D['id'].unique()
        PV_weather_1D_fid_df = pd.DataFrame()
        PV_weather_1D = pd.DataFrame()
        for nid in id_vec:

            PV_weather_nid = PV_weather_2D.loc[PV_weather_2D['id'] == nid]
            PV_weather_1D_fid = self.interpol_1d(list(PV_weather_nid['time']), PV_weather_nid['radiation'], list(futures))

            PV_weather_1D_fid_df['id'] = [nid] * futures.__len__()
            PV_weather_1D_fid_df['time'] = list(futures)
            PV_weather_1D_fid_df['value'] = list(PV_weather_1D_fid)

            PV_weather_1D = PV_weather_1D.append(PV_weather_1D_fid_df)

        # - wind turbines
        id_vec = WT_weather_2D['id'].unique()
        WT_weather_1D_fid_df = pd.DataFrame()
        WT_weather_1D = pd.DataFrame()
        for nid in id_vec:
            WT_weather_nid = WT_weather_2D.loc[WT_weather_2D['id'] == nid]
            WT_weather_1D_fid = self.interpol_1d(list(WT_weather_nid['time']), WT_weather_nid['windspeed'], list(futures))

            WT_weather_1D_fid_df['id'] = [nid] * futures.__len__()
            WT_weather_1D_fid_df['time'] = list(futures)
            WT_weather_1D_fid_df['value'] = list(WT_weather_1D_fid)

            WT_weather_1D = WT_weather_1D.append(WT_weather_1D_fid_df)

        # formatting arrays to dict
        l_id = []
        l_ws = []
        l_rad = []
        l_wm = []
        l_wm_set = self.data_hist['windspeed']['height']
        for n_id in range(0, KW_data[KW_data_columns[0]].__len__()):
            l_id.append(KW_data[KW_data_columns[0]][n_id])

            if KW_data[KW_data_columns[1]][n_id] == 'Windturbine':
                l_ws_i = WT_weather_1D[WT_weather_1D['id'] == KW_data[KW_data_columns[0]][n_id]]['value'].tolist()
                l_ws.append(l_ws_i)
                l_wm.append(l_wm_set)
            else:
                l_ws.append(None)
                l_wm.append(None)

            if KW_data[KW_data_columns[1]][n_id] == 'Photovoltaik':
                l_rad_i = PV_weather_1D[PV_weather_1D['id'] == KW_data[KW_data_columns[0]][n_id]]['value'].tolist()
                l_rad.append(l_rad_i)
            else:
                l_rad.append(None)

        KW_weather_data = {'id': l_id,
                           'windspeed': l_ws,
                           'radiation': l_rad,
                           'windmesshoehe': l_wm}

        return KW_weather_data

    # 2D Interpolation - based on 2D Interpolation of European_power_plant
    @staticmethod
    def interpol_2d(db_lat, db_long, db_values, kw_lat, kw_long):
        """
        This function interpolates in a grid of points (db_lat,db_long) with assigned values (db_values).
        It interpolates for points given by (kw_lat, kw_long) and outputs their corresponding value.

        Values inside the grid are interpolated linearly and values outside of the grid are interpolated
        to the nearest point of the grid.

        ATTENTION: If there are less than 3 points in db_... no grid can be formed and everything will be "interpolated"
                   to nearest.
                   Also, it is not allowed to have all points forming a line, they must span a 2dimensional space

        |  "db_" inputs are things as KEV, fuel costs or similar
        |  "kw_" inputs denote the power plants

        INPUTS:
            |  db_lat: Latitude, list of [float]; nx1
            |  db_long: Longitude, list of [float]; nx1
            |  db_values: list of [float]; nx1
            |  kw_lat: Latitude, list of [float]; jx1
            |  kw_long: Longitude, list of [float]; jx1

        OUTPUTS:
            kw_values: ndarray of [float]; jx1
            interp_values: ""
        """

        # arrange inputs for griddata
        xi = np.vstack((kw_lat, kw_long))
        gridpoints = np.vstack((db_lat, db_long))
        np_values = np.array(db_values)

        # interpolate
        interp_nearest = griddata(gridpoints.T, np_values.T, xi.T, method='nearest')

        if np_values.size < 3:
                interp_values = interp_nearest
        else:
            interp_linear = griddata(gridpoints.T, np_values.T, xi.T, method='linear')
            interp_values = np.where(np.isnan(interp_linear), interp_nearest, interp_linear)

        return interp_values

    # 1D Interpolation - based on 1D interpolation of European Power Plant
    @staticmethod
    def interpol_1d(db_time, db_values, kw_time):
        """
        This function interpolates in one dimension.
        |  X: time
        |  Y: values
        |  xi: kw_time
        |  yi: kw_values (output)

        Values inside [X(min), X(max)] are interpolated linearly,
        values outside of it are interpolated to the nearest X.
        If only one value for X and Y is provided, the output array is filled with the input value (nearest)

        INPUTS:
            |  time: list of [datetime]; nx1 (n>=2)
            |  values: list of [float]; nx1 (n>=2)
            |  kw_time: list of [datetime]; mx1 (m>=1)

        OUTPUTS:
            kw_values: ndarray of [float]; mx1
            interp_values: ""
        """

        # arrange inputs for griddata
        db_timestamp = np.array(db_time)
        kw_timestamp = np.array(kw_time)
        np_values = np.array(db_values)

        if db_timestamp.size > 1:
            # interpolate
            interp_nearest = griddata(db_timestamp.T, np_values.T, kw_timestamp.T, method='nearest')
            interp_linear = griddata(db_timestamp.T, np_values.T, kw_timestamp.T, method='linear')

            # replace Nan in linear with nearest (out of range values)
            interp_values = np.where(np.isnan(interp_linear), interp_nearest, interp_linear)

        else:
            # if only one time and one value is provided, set output to nearest (which in this case is the input value)
            interp_values = np.full(kw_time.size, db_values[0])

        return interp_values

    def future_weather_data(self, weather_data):

        # extract latitudes and longitudes
        lat_vec = self.data_hist["lat"]
        lon_vec = self.data_hist["lon"]

        # extract data for each point
        weather_list = []
        for ni in range(0, len(lat_vec)):
            weather_i = weather_data[(weather_data[:, 0] == lat_vec[ni]) & (weather_data[:, 1] == lon_vec[ni])]
            weather_i = weather_i[:, 2:6].tolist()
            weather_list.append(weather_i)

        dict_weather = {"ids": self.data_hist["ids"],
                        "lat": lat_vec,
                        "lon": lon_vec,
                        "weather": weather_list}

        # output
        #future_weather_data = weather_data.tolist()
        future_weather_data = dict_weather
        return future_weather_data

if __name__ == "__main__":

    # input
    # - date
    #start_date_i = datetime(2018, 12, 1, 0, 0, tzinfo=timezone('UTC'))
    #end_date_i = datetime(2018+1, 2, 1, 0, 0, tzinfo=timezone('UTC'))
    start_date_i = datetime(2018, 7, 17, 17, 15, tzinfo=timezone('UTC'))
    end_date_i = datetime(2018+1, 7, 18, 12, 0, tzinfo=timezone('UTC'))
    dt = 15*60
    step = timedelta(seconds=dt)
    date_series = []
    while start_date_i <= end_date_i:
        date_series.append(start_date_i)
        start_date_i += step
    date_series = [datetime2utc_time(x) for x in date_series]

    # - KW
    data_KW = {'id': [1, 2, 3, 4, 5, 6, 8, 10, 11, 12, 13, 14],
               'fk_kwt': [2, 1, 2, 1, 2, 1, 5, 3, 3, 6, 4, 4],
               'kw_bezeichnung': ['Windturbine', 'Photovoltaik', 'Windturbine', 'Photovoltaik', 'Winturbine', 'Photovoltaik', 'Others', 'Laufwasserkraftwerk',
                                       'Laufwasserkraftwerk', 'Others', 'Speicherwasserkraftwerk',
                                       'Speicherwasserkraftwerk'],
               'power': [1000000, 2000000, 3000000, 4000000, 5000000, 6000000, 8000000, 10000000, 11000000,
                              12000000, 13000000, 14000000],
               'spez_info': [{'NH': 150, 'Z0': 0.03}, {}, {'NH': 100, 'Z0': 0.2}, {}, {'NH': 250, 'Z0': 0.03}, {},
                                  {}, {}, {}, {}, {}, {}, ],
               'capex': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
               'opex': [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.12],
               'longitude': [-7, 0, 5, -4, 7, 8, 8, 15, 23, 22, 16.5, 20],
               'latitude': [40, 40, 45, 44, 52, 53, 46, 40, 40, 52, 50, 48]
               }

    # - mode
    islive_input = False

    # properties
    T_offset = 0
    u_offset = 0
    P_offset = 0
    ref_year = 2008

    props = {'ref_year': ref_year, 'T_offset': T_offset, 'u_offset': u_offset, 'P_offset': P_offset}
    inputs = {'date': date_series, 'KW': data_KW, 'mode': islive_input}
    outputs = Model.test(inputs, props)
