from core import Supermodel
from core.util import Input, Output, Property
import csv
import pandas as pd
from datetime import datetime
from Models._utils.time import utc_time2datetime, datetime2utc_time
import numpy as np
import json

# define the model class and inherit from class "Supermodel"
class Model(Supermodel):
    # model constructor
    def __init__(self, model_id, name: str):
        # instantiate supermodel
        super(Model, self).__init__(model_id, name)

        # define inputs
        #self.inputs['v'] = Input('wind speed')
        #self.inputs['dir'] = Input('wind direction')

        # define outputs
        #self.outputs['p_el'] = Output('electrical power')
        #self.outputs['f_rot'] = Output('rotor frequency')

        # define properties
        #self.properties['h_hub'] = Property('hub height', default=10, data_type=float)
        #self.properties['d'] = Property('diameter', default=10, data_type=float)


        # define persistent variables
        #self.pers_variable_0 = 5

    async def func_birth(self):

        # Infos
        filename = 'history_export_FHNW_2006_2017csv_Info.csv'
        data_info_table = pd.read_csv(filename, sep=';', header=None)
        id_list = list(data_info_table.values[3][4:29])
        lat_list = data_info_table.values[0][4:29]
        lat_list = [float(x) for x in lat_list]
        lat_list = list(lat_list)
        lon_list = list(data_info_table.values[1][4:29])
        lon_list = [float(x) for x in lon_list]
        lon_list = list(lon_list)
        asl_list = list(data_info_table.values[2][4:29])
        asl_list = [float(x) for x in asl_list]
        asl_list = list(asl_list)
        temp_height = 2.
        wind_height = 10.
        rad_height = 0.
        temp_unit = 'Celsius'
        wind_unit = 'm/s'
        rad_unit = 'W/m2'

        # Data
        filename = 'history_export_FHNW_2006_2017csv_Data.csv'
        data_table = pd.read_csv(filename, sep=';', header=0)
        # - time
        time_list = []
        for it in range(0, data_table.__len__()):
            xi = datetime(data_table.Year[it], data_table.Month[it], data_table.Day[it], data_table.Hour[it])
            time_list.append(xi)
        time_list = [datetime2utc_time(x) for x in time_list]
        time_list = list(time_list)

        # - temperature
        temp_array = data_table.values[:, 4:29]
        temp_array = temp_array.transpose()
        temp_list = temp_array.tolist()

        # - wind speed
        wind_array = data_table.values[:, 29:54]
        wind_array = wind_array.transpose()
        wind_list = wind_array.tolist()

        # - radiation
        rad_array = data_table.values[:, 54:79]
        rad_array = rad_array.transpose()
        rad_list = rad_array.tolist()

        # dict
        dict_hist = {"ids": id_list,
                     "lat": lat_list,
                     "lon": lon_list,
                     "asl": asl_list,
                     "times": time_list,
                     "temperature": {"height": temp_height,
                                     "unit": temp_unit,
                                     "values": temp_list},
                     "windspeed": {"height": wind_height,
                                     "unit": wind_unit,
                                     "values": wind_list},
                     "radiation": {"height": rad_height,
                                   "unit": rad_unit,
                                   "values": rad_list}
                     }
        #json_dumps = json.dumps(dict_hist)
        with open('dict_hist', 'w') as fp:
            json.dump(dict_hist, fp)

        # dict of weather point info data
        dict_weather_points = {"ids": id_list,
                               "lat": lat_list,
                               "lon": lon_list,
                               "asl": asl_list
                               }
        with open('dict_weather_points', 'w') as fp:
            json.dump(dict_weather_points, fp)


        return 1




if __name__ == "__main__":

    inputs = {}
    properties = {}

    outputs = Model.test(inputs, properties)




