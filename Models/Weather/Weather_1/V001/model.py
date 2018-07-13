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
        self.outputs['KW_weather'] = Output(name='weather data of KWs', unit='date, °C, m/s, ???', info='????')
        self.outputs['Futures_weather'] = Output(name='future weather data (temperature, wind speed, radiation)', unit='date, °C, m/s, ???', info='????')

        # define properties
        self.properties['T_offset'] = Property(default=0., data_type=float, name='temperature offset', unit='%', info="offset of temperature in %")
        self.properties['u_offset'] = Property(default=0., data_type=float, name='wind speed offset', unit='%', info="offset of wind speed in %")
        self.properties['P_offset'] = Property(default=0., data_type=float, name='radiation offset', unit='%', info="offset of radiation in %")
        self.properties['ref_year'] = Property(default=2007, data_type=int, name='reference year', unit='-', info="reference year for modeled weather")

        # define persistent variables
        self.data_hist = None
        self.data_hist_year = None
        self.ref_year = None

    async def func_birth(self):
        self.data_hist = self.historic_data_read()
        #pass

    async def func_amend(self, keys=[]):

        if 'ref_year' in keys:
            self.ref_year = self.get_property('ref_year')
            self.data_hist_year = self.historic_select_year(self.data_hist, self.ref_year)

    async def func_peri(self, prep_to_peri=None):

        # get inputs
        islife = await self.get_input('mode')
        KW_data_orig = await self.get_input('KW')
        KW_data = {k: KW_data_orig[k] for k in ('id', 'kw_bezeichnung', 'latitude', 'longitude')}
        futures = await self.get_input('date')

        # prepare weather data
        islife = False
        if islife:
            weather_data = self.prepare_API_weather()
        else:
            weather_data = self.prepare_historic_weather(futures)

        # KW weather
        KW_weather_data = self.KW_weather_data(KW_data, weather_data, futures)


        # futures weather
        futures_weather_data = 1 #self.future_weather_data(futures, weather_data)

        # set output
        self.set_output("KW_weather", KW_weather_data)
        self.set_output("Futures_weather", futures_weather_data)

    @staticmethod
    def historic_data_read():

        path = os.path.abspath(__file__)
        dir_path = os.path.dirname(path)
        filename = os.path.join(dir_path, 'confidential', 'dict_hist')
        with open(filename, 'r') as f:
            data_hist = json.load(f)
        return data_hist

    @staticmethod
    def historic_select_year(data_hist, ref_year):
        # data = copy.deepcopy(data_hist_i)
        # data = json.loads(json.dumps(data_hist_i))
        # data = self.historic_data_read()
        # data = data_hist_i
        data = dict((k, v) for k, v in data_hist.items())

        start_date = datetime(ref_year, 1, 1, 0, 0)
        start_date = datetime2utc_time(start_date)
        end_date = datetime(ref_year+1, 1, 1, 0, 0)
        end_date = datetime2utc_time(end_date)

        time = np.array(data["times"])
        time = time[np.newaxis, :]
        temp = np.array(data["temperature"]["values"])
        wind = np.array(data["windspeed"]["values"])
        rad = np.array(data["radiation"]["values"])

        matrix = np.append(time, temp, axis=0)
        matrix = np.append(matrix, wind, axis=0)
        matrix = np.append(matrix, rad, axis=0)
        matrix = matrix.transpose()
        matrix = matrix[(matrix[:, 0] >= start_date) & (matrix[:, 0] <= end_date)]
        matrix = matrix.transpose()

        data["times"] = matrix[0, :].tolist()
        # a = np.array([[utc_time2datetime(x) for x in data["times"]]]).transpose()
        data["temperature"]["values"] = matrix[1:26, :].tolist()
        data["windspeed"]["values"] = matrix[26:51, :].tolist()
        data["radiation"]["values"] = matrix[51:76, :].tolist()

        return data

    def prepare_API_weather(self):

        filepath = "confidential/API_Key"
        #filepath = "Models/Weather/Weather_1/V001/confidential/API_Key"
        with open(filepath, "r") as f:
            API_key = f.readline()
        url_ad = API_key
        #weather_API_read = requests.get(url_ad).json()

        #with open('confidential/dict_API', 'w') as fp:
        #    json.dump(weather_API_read, fp)

    def prepare_historic_weather(self, futures):

        # set futures back to ref_year
        futures_shifted = self.dates_shift(futures)

        # filter historic weather data
        data_filtered = self.data_filter(futures_shifted)

        # create data base of historic weather data
        data_base = self.create_database(data_filtered)

        # forecast weather data (shift of historic weather data)
        #forecast_data = self.datahist_shift(data_base, futures[0])

        return data_base            # forecast_data

    def dates_shift(self, dates):
        dates = [utc_time2datetime(x) for x in dates]
        date_1 = dates[0]
        date_1_ref = date_1.replace(year=self.ref_year)
        date_shift = date_1-date_1_ref
        dates_shifted = [x-date_shift for x in dates]
        year_1 = dates_shifted[0].year
        # year_end = dates_shifted[dates_shifted.__len__()].year
        # if year_1 != year_end:
        dates_shifted = [x.replace(year=year_1) for x in dates_shifted]
        dates_shifted = [datetime2utc_time(x) for x in dates_shifted]

        return dates_shifted

    def data_filter(self, dates):

        data = {k: v for k, v in self.data_hist_year.items()}
        ref_times = data['times']
        ref_times = np.array(ref_times)

        # first and last date
        date_first = dates[0]
        date_last = dates[len(dates)-1]

        date_before_first = np.max(ref_times[ref_times <= date_first])
        date_after_last = np.min(ref_times[ref_times >= date_last])

        # create data matrix
        time = np.array(data["times"])
        time = time[np.newaxis, :]
        temp = np.array(data["temperature"]["values"])
        wind = np.array(data["windspeed"]["values"])
        rad = np.array(data["radiation"]["values"])

        matrix = np.append(time, temp, axis=0)
        matrix = np.append(matrix, wind, axis=0)
        matrix = np.append(matrix, rad, axis=0)
        matrix = matrix.transpose()

        # filter
        # - within a year
        if date_first < date_last:
            # filtered_ref_times = ref_times[(ref_times >= date_before_first) & (ref_times <= date_after_last)]
            matrix = matrix[(matrix[:, 0] >= date_before_first) & (matrix[:, 0] <= date_after_last)]

        # - turn of the year
        else:
            # filtered_ref_times = ref_times[(ref_times <= date_after_last) | (ref_times >= date_before_first)]
            matrix = matrix[(matrix[:, 0] <= date_after_last) | (matrix[:, 0] >= date_before_first)]

        matrix = matrix.transpose()

        # update dict
        data2 = {"ids": data["ids"], "lat": data["lat"], "lon": data["lon"], "asl": data["asl"],
                 "times": matrix[0, :].tolist(),
                 "temperature": {'height': data["temperature"]['height'],
                                 'unit': data["temperature"]['unit'],
                                 "values": matrix[1:26, :].tolist()},
                 "windspeed": {'height': data["windspeed"]['height'],
                               'unit': data["windspeed"]['unit'],
                               "values": matrix[26:51, :].tolist()},
                 "radiation": {'height': data["radiation"]['height'],
                               'unit': data["radiation"]['unit'],
                               "values": matrix[51:76, :].tolist()}
                 }
        '''
        data2[] = data["ids"]
        data2["lat"] = data["lat"]
        data2["lon"] = data["lon"]
        data2["asl"] = data["asl"]
        data2["times"] = matrix[0, :].tolist()
        data2["temperature"]=dict()
        data2["temperature"]['height'] = data["temperature"]['height']
        data2["temperature"]['unit'] = data["temperature"]['unit']
        data2["temperature"]["values"] = matrix[1:26, :].tolist()
        data2["windspeed"]=dict()
        data2["windspeed"]['height'] = data["windspeed"]['height']
        data2["windspeed"]['unit'] = data["windspeed"]['unit']
        data2["windspeed"]["values"] = matrix[26:51, :].tolist()
        data2["radiation"]=dict()
        data2["radiation"]['height'] = data["radiation"]['height']
        data2["radiation"]['unit'] = data["radiation"]['unit']
        data2["radiation"]["values"] = matrix[51:76, :].tolist()
        '''
        return data2

    @staticmethod
    def create_database(data_filtered):

        num_points = data_filtered["lat"].__len__()
        num_times = data_filtered["times"].__len__()
        lat_vec = []
        lon_vec = []
        time_vec = np.tile(np.array(data_filtered["times"]), num_points)
        temp_vec = []
        wind_vec = []
        rad_vec = []
        for it in range(0, num_points):
            lat_vec.append(np.repeat(data_filtered["lat"][it], num_times))
            lon_vec.append(np.repeat(data_filtered["lon"][it], num_times))

            temp_vec.append(data_filtered["temperature"]["values"][it])
            wind_vec.append(data_filtered["windspeed"]["values"][it])
            rad_vec.append(data_filtered["radiation"]["values"][it])

        # change format to array
        lat_vec = np.array([lat_vec]).ravel()
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

        data_base = np.concatenate((lat_vec, lon_vec, time_vec, temp_vec, wind_vec, rad_vec), axis=1)

        return data_base

    # def datahist_shift(self, datahist, future_start):

    #
    #    future_1 = utc_time2datetime(future_start)
    #    future_1_ref = future_1.replace(year=self.ref_year)
    #    date_shift = future_1-future_1_ref
    #    print(date_shift)
    #
    #    hist_time = datahist[:, 2]
    #    hist_time = [utc_time2datetime(x) for x in hist_time]
    #    hist_time_shifted = [x+date_shift for x in hist_time]
    #    hist_time_shifted = [datetime2utc_time(x) for x in hist_time_shifted]
    #
    #    forecast_weather = datahist
    #    forecast_weather[:, 2] = hist_time_shifted
    #
    #    return forecast_weather

    def KW_weather_data(self, KW_data, weather_data, futures):

        KW_data_columns = ['id', 'kw_bezeichnung', 'latitude', 'longitude']

        # shift futures back
        futures = self.dates_shift(futures)

        KW_data_df = pd.DataFrame(KW_data)
        WT_data = KW_data_df.loc[KW_data_df[KW_data_columns[1]] == 'Windturbine']
        PV_data = KW_data_df.loc[KW_data_df[KW_data_columns[1]] == 'Photovoltaik']

        weather_df = pd.DataFrame(data=weather_data, columns=['lat', 'lon', 'time', 'temperature', 'windspeed', 'radiation'])
        weather_PV = weather_df[['lat', 'lon', 'time', 'radiation']]
        weather_WT = weather_df[['lat', 'lon', 'time', 'windspeed']]

        # 2D interpolation over lat/lon
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

        # 1D interpolation over time
        # - PV
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

        # - WT
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

        # format
        l_id = []
        l_ws = []
        l_rad = []
        l_wm = []
        l_wm_set = self.data_hist['windspeed']['height']
        for n_id in range(0, KW_data[KW_data_columns[0]].__len__()):
            l_id.append(KW_data[KW_data_columns[0]][n_id])

            if KW_data[KW_data_columns[1]][n_id] is 'Windturbine':
                l_ws_i = WT_weather_1D[WT_weather_1D['id'] == KW_data[KW_data_columns[0]][n_id]]['value'].tolist()
                l_ws.append(l_ws_i)
                l_wm.append(l_wm_set)
            else:
                l_ws.append(None)
                l_wm.append(None)

            if KW_data[KW_data_columns[1]][n_id] is 'Photovoltaik':
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

        #if db_values.size < 3:
        if np_values.size < 3:
                interp_values = interp_nearest
        else:
            #interp_linear = griddata(gridpoints.T, db_values.T, xi.T, method='linear')
            interp_linear = griddata(gridpoints.T, np_values.T, xi.T, method='linear')
            # replace Nan in linear with nearest (out of range values)
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

        # format
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

    def future_weather_data(self, futures, weather_data):

        future_weather_data = 1
        return future_weather_data

if __name__ == "__main__":

    # input
    # - date
    start_date_i = datetime(2018, 12, 1, 0, 0, tzinfo=timezone('UTC'))
    end_date_i = datetime(2018+1, 2, 1, 0, 0, tzinfo=timezone('UTC'))
    dt = 15*60
    step = timedelta(seconds=dt)
    date_series = []
    while start_date_i <= end_date_i:
        date_series.append(start_date_i)
        start_date_i += step
    date_series = [datetime2utc_time(x) for x in date_series]

    # - KW
    # data_KW = {"lat": [40, 50],
    #           "lon": [0, 10]}
    # data_KW = {"lat": [40],
    #           "lon": [0]}
    data_KW = {'id': [1, 2, 3, 4, 5, 6, 8, 10, 11, 12, 13, 14],
               'fk_kwt': [2, 1, 2, 1, 2, 1, 5, 3, 3, 6, 4, 4],
               'kw_bezeichnung': ['WT', 'PV', 'WT', 'PV', 'WT', 'PV', 'Others', 'Laufwasserkraftwerk',
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
    islife_input = False

    # properties
    T_offset = 0
    u_offset = 0
    P_offset = 0
    ref_year = 2008

    props = {'ref_year': ref_year, 'T_offset': T_offset, 'u_offset': u_offset, 'P_offset': P_offset}
    inputs = {'date': date_series, 'KW': data_KW, 'mode': islife_input}
    outputs = Model.test(inputs, props)
