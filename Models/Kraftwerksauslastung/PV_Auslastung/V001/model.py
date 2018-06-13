from core import Supermodel
from core.util import Input, Output, Property


# define the model class and inherit from class "Supermodel"
class Model(Supermodel):
    # model constructor
    def __init__(self, id, name: str):
        # instantiate supermodel
        super(Model, self).__init__(id, name)

        # define inputs
        self.inputs['weather'] = Input({'name': 'WeatherData'})
        self.inputs['kwDaten'] = Input({'name': 'PowerPlantsData'})

        # define outputs
        self.outputs['load'] = Output({'name': 'Load'})

    async def func_peri(self, prep_to_peri=None):
        # get inputs
        weather = await self.get_input('weather')
        kwDaten = await self.get_input('kwDaten')

        load = self.calc_load(weather, kwDaten)

        # set output
        self.set_output("load", load)



    # define additional methods (normal)
    def calc_load(self, weather_data, kw_data):
        load = weather_data * kw_data
        return load



