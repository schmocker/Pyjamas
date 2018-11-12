import asyncio
from core.util import Input, Output, Property
from core.supermodel import Supermodel
import json


class Model(Supermodel):
    """
        plot time series, historical and forecast
    """

    def __init__(self, uuid, name :str):
        super(Model, self).__init__(uuid,name)

        self.inputs['times'] = Input(name='Times', unit='s', info='utc time array')
        self.inputs['values'] = Input(name='Values', unit='any', info='value array')

        self.outputs['data_histfore'] = Output(name='Historical and forecast data', unit='div',
                                               info='{time_hist, time_forecast, value_hist, value_forecast}')
        self.outputs['y_scaling'] = Output(name='Scaling of y axis', unit='', info='Scaling of y axis')
        self.outputs['y_label'] = Output(name='y label', unit='', info='Label of y axis')

        self.properties["filter"] = Property(default='', data_type=str, name='Location',
                                             unit='-', info='Location',
                                             example='Baden')
        self.properties["num_hist"] = Property(default=0, data_type=int, name='Number historical data', unit='-',
                                               info='Number of historical data to be saved (0=unlimited)', example='100')
        self.properties["scaling"] = Property(default=1, data_type=float, name='Scaling factor', unit='-',
                                              info='Scaling factor for y axis', example='1e-9')
        self.properties["y_labeling"] = Property(default='Property', data_type=str, name='y label', unit='-',
                                                 info='Label for y axis', example='Demand [GW]')

        self.data_hist_forecast = {"historic": {}, "forecast": {}}
        self.data_hist_forecast["historic"]["time"] = []
        self.data_hist_forecast["historic"]["value"] = []
        self.data_hist_forecast["forecast"]["time"] = []
        self.data_hist_forecast["forecast"]["value"] = []

        self.y_scaling = None
        self.y_labeling = None

    async def func_amend(self, keys=[]):

        if 'scaling' in keys:
            self.y_scaling = self.get_property("scaling")

        if 'y_labeling' in keys:
            self.y_labeling = self.get_property("y_labeling")


    async def func_peri(self, prep_to_peri=None):
        times = await self.get_input("times")
        values = await self.get_input("values")

        fil = self.get_property("filter")
        #fil = json.loads('[' + fil + ']')
        #for f in fil:
        #    values = values[f]
        i_stao = values['distribution_networks'].index(fil)
        values = values['prices'][i_stao]

        self.data_hist_forecast["forecast"]["time"] = times
        self.data_hist_forecast["forecast"]["value"] = values
        self.data_hist_forecast["historic"]["time"].append(times[0])
        self.data_hist_forecast["historic"]["value"].append(values[0])

        num_hist = self.get_property("num_hist")
        # test length of historical data
        if (num_hist>=0 & num_hist<self.data_hist_forecast["historic"]["value"].__len__()):
            self.data_hist_forecast["historic"]["time"] = self.data_hist_forecast["historic"]["time"][-num_hist:]
            self.data_hist_forecast["historic"]["value"] = self.data_hist_forecast["historic"]["value"][-num_hist:]

        self.set_output("data_histfore", self.data_hist_forecast)
        self.set_output("y_scaling", self.y_scaling)
        self.set_output("y_label", self.y_labeling)


if __name__ == "__main__":
    inputs = {
        'times': [1,2,3,4],
        'values': {'hallo': [[4,5,6,7],[4,5,6,7],[4,5,6,7]], 'du': [9,8,7,6]}
    }

    properties = {
        'filter': '"hallo" ,2',
        'num_hist': 2
    }

    outputs = Model.test(inputs, properties)

    print(outputs)
