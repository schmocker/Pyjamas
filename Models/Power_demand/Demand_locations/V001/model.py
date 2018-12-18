from pyjamas_core import Supermodel
from pyjamas_core.util import Input, Output, Property
import os
import pandas as pd

# define the model class and inherit from class "Supermodel"
class Model(Supermodel):
    # model constructor
    def __init__(self, id, name: str):
        # instantiate supermodel
        super(Model, self).__init__(id, name)

        # define inputs

        # define outputs
        self.outputs['Demand_loc'] = Output(name='Demand locations', unit='{id: [], Country: [] Latitude: [], Longitude []}',
                                            info='Demand locations with their id, country, latitude and longitude')

        # define properties
        # - distribution network
        #self.properties['distNets'] = Property(default='{"Baden": {"Lat": 47.47256, "Lon": 8.30850}}', data_type=str, name='distribution network', unit='-',
        #                                      info="Distribution network with lon and lat",
        #                                      example='{"Baden": {"Lat": 47.47256, "Lon": 8.30850}, '
        #                                               '"Brugg": {"Lat": 47.48420, "Lon": 8.20706}, '
        #                                               '"Olten": {"Lat": 47.35212, "Lon": 7.90801}}')

        # define persistent variables
        self.demand_loc = None


    async def func_birth(self):
        #await self.func_amend(['distNets'])

        demand_loc = {'id': [], 'country': [], 'lat': [], 'lon': []}

        # read historic weather data
        path = os.path.abspath(__file__)
        dir_path = os.path.dirname(path)
        filename = os.path.join(dir_path, 'List_country_locations')
        data_loc = pd.read_csv(filename, sep=',')

        demand_loc['id'] = data_loc['id'].tolist()
        demand_loc['country'] = data_loc['country'].tolist()
        demand_loc['lat'] = data_loc['latitude'].tolist()
        demand_loc['lon'] = data_loc['longitude'].tolist()

        self.demand_loc = demand_loc


    #async def func_amend(self, keys=[]):
    #    if 'distNets' in keys:
    #        distNets_prop = self.get_property('distNets')
    #        dict_distNets = json.loads(distNets_prop)
    #
    #        # formatting
    #        locations = list(dict_distNets.keys())
    #        list_lat = [dict_distNets[x]["Lat"] for x in locations]
    #        list_lon = [dict_distNets[x]["Lon"] for x in locations]
    #
    #        # test uniqueness
    #        for it in range(1, locations.__len__()):
    #            #print(locations[it])
    #            for jt in range(1,it):
    #                if locations[it] == locations[jt]:
    #                    locations[it] = locations[it] + "_1"
    #
    #        # output
    #        output = {"dist_networks": locations, "Latitude": list_lat, "Longitude": list_lon}
    #
    #        self.distNets = output

    async def func_peri(self, prep_to_peri=None):
        self.set_output('Demand_loc', self.demand_loc)
