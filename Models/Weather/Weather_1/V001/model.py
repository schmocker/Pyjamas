from core import Supermodel
from core.util import Input, Output, Property
import csv
from datetime import datetime, timedelta
from Models._utils.time import datetime2utc_time, utc_time2datetime
import numpy as np
from pytz import timezone
from scipy.interpolate import griddata
import json
import copy

# define the model class and inherit from class "Supermodel"
class Model(Supermodel):
    # model constructor
    def __init__(self, id, name: str):
        # instantiate supermodel
        super(Model, self).__init__(id, name)

        # define inputs
        #self.inputs['mode'] = Input(name='modus', unit='-', info="modus (live or simulation)")
        #self.inputs['KW'] = Input(name='KW info', unit='-', info="KW information (id, lat, lon)")
        self.inputs['date'] = Input(name='Time vector', unit='s', info="Time in utc")

        # define outputs
        #self.outputs['weather_data'] = Output(name='weather data of KWs', unit='date, °C, m/s, ???', info='????')

        # define properties
        #self.properties['T_offset'] = Property(default=0., data_type=float, name='temperature offset', unit='%', info="offset of temperature in %")
        #self.properties['u_offset'] = Property(default=0., data_type=float, name='wind speed offset', unit='%', info="offset of wind speed in %")
        #self.properties['P_offset'] = Property(default=0., data_type=float, name='radiation offset', unit='%', info="offset of radiation in %")
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
            ii = self.historic_data_read()
            self.data_hist_year = self.historic_select_year(ii, self.ref_year)
            r=5

    async def func_peri(self, prep_to_peri=None):

        # get inputs
        #mode = await self.get_input('mode')
        #KW_data = await self.get_input('KW')
        dates = await self.get_input('date')

        # set dates back to ref_year
        dates = [utc_time2datetime(x) for x in dates]
        dates = [d.replace(year=self.ref_year) for d in dates]
        dates = [datetime2utc_time(x) for x in dates]

        ref_times = self.data_hist_year['times']
        ref_times = np.array(ref_times)

        # first and last date
        date_first = dates[0]
        date_last = dates[dates.__len__()-1]

        date_before_first = np.max(ref_times[ref_times <= date_first])
        date_after_last = np.min(ref_times[ref_times >= date_last])

        # normalfall
        if date_first<date_last:
            filered_ref_times = ref_times[(ref_times >= date_before_first) & (ref_times <= date_after_last)]

        # jahresübergang
        else:
            filered_ref_times = ref_times[(ref_times <= date_after_last) | (ref_times >= date_before_first)]

        b = [utc_time2datetime(t,timezone('UTC')) for t in filered_ref_times]

#        #date_min = utc_time2datetime(date_min)
        #date_max = utc_time2datetime(date_max)
        #date_min.replace(minute=0)
        #date_max = date_max.replace(minute=0)+timedelta(hours=1)

        # select hist_data within first and last date
        # hist_interval = self.data_hist_year
        # hist_interval = self.historic_select_interval(hist_interval, date_min, date_max)

        r=5





    @staticmethod
    def historic_data_read():

        filename = 'dict_hist'
        with open(filename, 'r') as f:
            data_hist = json.load(f)
        return data_hist

    @staticmethod
    def historic_select_year(data_hist_i, ref_year):
        #data = copy.deepcopy(data_hist_i)
        #data = json.loads(json.dumps(data_hist_i))
        #data = self.historic_data_read()
        data = data_hist_i

        #start_date = datetime(ref_year - 1, 12, 1, 1, 0)
        start_date = datetime(ref_year, 1, 1, 0, 0)
        start_date = datetime2utc_time(start_date)
        #end_date = datetime(ref_year + 1, 2, 1, 0, 0)
        end_date = datetime(ref_year+1, 1, 1, 0, 0)
        end_date = datetime2utc_time(end_date)

        time = np.asarray(data_hist_i["times"])
        time = time[np.newaxis, :]
        temp = np.asarray(data_hist_i["temperature"]["values"])
        wind = np.asarray(data_hist_i["windspeed"]["values"])
        rad = np.asarray(data_hist_i["radiation"]["values"])

        matrix = np.append(time, temp, axis=0)
        matrix = np.append(matrix, wind, axis=0)
        matrix = np.append(matrix, rad, axis=0)
        matrix = matrix.transpose()
        matrix = matrix[(matrix[:, 0] >= start_date) & (matrix[:, 0] <= end_date)]
        matrix = matrix.transpose()

        data["times"] = matrix[0, :].tolist()
        a = np.array([[utc_time2datetime(x) for x in data["times"]]]).transpose()
        data["temperature"]["values"] = matrix[1:26, :].tolist()
        data["windspeed"]["values"] = matrix[26:51, :].tolist()
        data["radiation"]["values"] = matrix[51:76, :].tolist()

        return data




if __name__ == "__main__":



    #hist = Model.historic_data_read()
    #hist_sel = Model.historic_select_year(hist, 2008)

    #r=1

    # input
    start_date = datetime(2018, 12, 1, 0, 0, tzinfo=timezone('UTC'))
    end_date = datetime(2018+1, 2, 1, 0, 0, tzinfo=timezone('UTC'))
    dt = 15*60
    step = timedelta(seconds=dt)
    date_series = []
    while start_date <= end_date:
        date_series.append(start_date)
        start_date += step
    date_series = [datetime2utc_time(x) for x in date_series]

    props = {'ref_year':2008}
    inputs = {'date':date_series}
    outputs = Model.test(inputs, props)