from core import Supermodel
from core.util import Input, Output, Property
from datetime import datetime, timedelta
from Models._utils.time import datetime2utc_time, utc_time2datetime
import numpy as np
from pytz import timezone
import json


# define the model class and inherit from class "Supermodel"
class Model(Supermodel):
    # model constructor
    def __init__(self, id, name: str):
        # instantiate supermodel
        super(Model, self).__init__(id, name)

        # define inputs
        # self.inputs['mode'] = Input(name='modus', unit='-', info="modus (live or simulation)")
        # self.inputs['KW'] = Input(name='KW info', unit='-', info="KW information (id, lat, lon)")
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
        # KW_data = await self.get_input('KW')
        dates = await self.get_input('date')

        # set dates back to ref_year
        dates = [utc_time2datetime(x) for x in dates]
        dates = [d.replace(year=self.ref_year) for d in dates]
        dates = [datetime2utc_time(x) for x in dates]

        # filter data
        data_filtered = self.data_filter(dates)

        # create data base
        data_base = self.create_database(data_filtered)



        r = 5
        print(r)

    @staticmethod
    def historic_data_read():

        filename = 'dict_hist'
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
        time_vec = np.repeat(np.array(data_filtered["times"]), num_points)
        temp_vec = []
        wind_vec = []
        rad_vec = []
        for it in range(0, 24):
            lat_vec = lat_vec.append(list(np.repeat(data_filtered["lat"][it], num_times)))
            lon_vec = lon_vec.append(list(np.repeat(data_filtered["lon"][it], num_times)))

            temp_vec = temp_vec.append(data_filtered["temperature"]["values"][it])
            wind_vec = wind_vec.append(data_filtered["windspeed"]["values"][it])
            rad_vec = rad_vec.append(data_filtered["radiation"]["values"][it])

        data_base = np.concatenate((lat_vec, lon_vec, time_vec, temp_vec, wind_vec, rad_vec), axis=0)


        return data_base


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

    props = {'ref_year': 2008}
    inputs = {'date': date_series}
    outputs = Model.test(inputs, props)
