from core import Supermodel
from core.util import Input, Output, Property
from datetime import datetime, timedelta
from Models._utils.time import datetime2utc_time, utc_time2datetime
import numpy as np
from pytz import timezone
import json
import math
from scipy.interpolate import griddata

# define the model class and inherit from class "Supermodel"
class Model(Supermodel):
    # model constructor
    def __init__(self, id, name: str):
        # instantiate supermodel
        super(Model, self).__init__(id, name)

        # define inputs
        # self.inputs['mode'] = Input(name='modus', unit='-', info="modus (live or simulation)")
        self.inputs['KW'] = Input(name='KW info', unit='-', info="KW information (id, lat, lon)")
        self.inputs['date'] = Input(name='Time vector', unit='s', info="Time in utc")

        # define outputs
        # self.outputs['weather_data'] = Output(name='weather data of KWs', unit='date, °C, m/s, ???', info='????')

        # define properties
        # self.properties['T_offset'] = Property(default=0., data_type=float, name='temperature offset', unit='%', info="offset of temperature in %")
        # self.properties['u_offset'] = Property(default=0., data_type=float, name='wind speed offset', unit='%', info="offset of wind speed in %")
        # self.properties['P_offset'] = Property(default=0., data_type=float, name='radiation offset', unit='%', info="offset of radiation in %")
        self.properties['ref_year'] = Property(default=2000, data_type=int, name='reference year', unit='-', info="reference year for modeled weather")

        # define persistent variables
        self.data_hist = None
        self.data_hist_year = None
        self.ref_year = None

    async def func_birth(self):
        # read historic weather data
        self.data_hist = self.historic_data_read()

    async def func_amend(self, keys=[]):

        if 'ref_year' in keys:
            self.ref_year = self.get_property('ref_year')
            self.data_hist_year = self.historic_select_year(self.data_hist, self.ref_year)

    async def func_peri(self, prep_to_peri=None):

        # get inputs
        # mode = await self.get_input('mode')
        KW_data = await self.get_input('KW')
        dates = await self.get_input('date')

        # set dates back to ref_year
        # dates = [utc_time2datetime(x) for x in dates]
        # dates = [d.replace(year=self.ref_year) for d in dates]
        # dates = [datetime2utc_time(x) for x in dates]
        dates = self.dates_shift(dates)

        # filter data
        data_filtered = self.data_filter(dates)

        # create data base
        data_base = self.create_database(data_filtered)

        # interpolation
        grid_pattern = {"lat": data_filtered["lat"],
                        "lon": data_filtered["lon"],
                        "times": data_filtered["times"]}
        data_interp = self.interpolation(grid_pattern, data_base, KW_data["lat"], KW_data["lon"], dates)





        r = 5
        print(r)

    @staticmethod
    def historic_data_read():

        filename = 'confidential/dict_hist'
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

    def data_filter(self, dates):

        data = dict((k, v) for k, v in self.data_hist_year.items())
        ref_times = data['times']
        ref_times = np.array(ref_times)

        # first and last date
        date_first = dates[0]
        date_last = dates[dates.__len__()-1]

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
        data["times"] = matrix[0, :].tolist()
        data["temperature"]["values"] = matrix[1:26, :].tolist()
        data["windspeed"]["values"] = matrix[26:51, :].tolist()
        data["radiation"]["values"] = matrix[51:76, :].tolist()

        return data

    @staticmethod
    def create_database(data_filtered):

        num_points = data_filtered["lat"].__len__()
        num_times = data_filtered["times"].__len__()
        lat_vec = []
        lon_vec = []
        time_vec = np.tile(np.array(data_filtered["times"]), num_points-1)
        temp_vec = []
        wind_vec = []
        rad_vec = []
        for it in range(0, 24):
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

    def check_leapyear(self, current_year):
        bool_leap_current_year = self.ind_leapyear(current_year)
        bool_leap_ref_year = self.ind_leapyear(self.ref_year)

        if bool_leap_current_year != bool_leap_ref_year:
            print("change reference year due to inconsistency of leap year")
            if bool_leap_current_year:
                self.ref_year = int(2012)        # or 2008, 2012, 2016
                print('')
            else:
                self.ref_year = int(self.ref_year+1) # instead of {2008, 2012, 2016} to {2009, 2013, 2017}

    @staticmethod
    def ind_leapyear(year_i):

        if year_i%4 == 0:
            if year_i%100 == 0:
                if year_i%400 == 0:
                    bool_leapyear = True
                else:
                    bool_leapyear = False
            else:
                bool_leapyear = True
        else:
            bool_leapyear = False

        return bool_leapyear

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

    def interpolation(self, grid_pattern, data_base, lat_x, lon_x, time_x):

        db_time = grid_pattern["times"]
        db_lat = grid_pattern["lat"]
        db_lon = grid_pattern["lon"]

        # interpolation of (lat, lon)
        for tt in db_time:
            data_tt = data_base[data_base[:, 2] == tt]
            data_T = data_tt[:, 3].tolist()
            data_u = data_tt[:, 4]
            data_r = data_tt[:, 5]

            data_T_interp = self.interpol_2d(db_lat, db_lon, data_T, lat_x, lon_x)





            r = 2

        r=1




        return data_interp

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
        """

        # arrange inputs for griddata
        xi = np.vstack((kw_lat, kw_long))
        gridpoints = np.vstack((db_lat, db_long))
        g_values = np.array(db_values)

        # interpolate
        interp_nearest = griddata(gridpoints.T, g_values.T, xi.T, method='nearest')

        if db_values.size < 3:
            kw_values = interp_nearest
        else:
            interp_linear = griddata(gridpoints.T, db_values.T, xi.T, method='linear')
            # replace Nan in linear with nearest (out of range values)
            kw_values = np.where(np.isnan(interp_linear), interp_nearest, interp_linear)

        return kw_values


if __name__ == "__main__":

    # input
    start_date_i = datetime(2018, 12, 1, 0, 0, tzinfo=timezone('UTC'))
    end_date_i = datetime(2018+1, 2, 1, 0, 0, tzinfo=timezone('UTC'))
    dt = 15*60
    step = timedelta(seconds=dt)
    date_series = []
    while start_date_i <= end_date_i:
        date_series.append(start_date_i)
        start_date_i += step
    date_series = [datetime2utc_time(x) for x in date_series]
    data_KW = {"lat": [40, 50],
               "lon": [0, 10]}
    data_KW = {"lat": [40],
               "lon": [0]}

    props = {'ref_year': 2008}
    inputs = {'date': date_series, 'KW': data_KW}
    outputs = Model.test(inputs, props)
