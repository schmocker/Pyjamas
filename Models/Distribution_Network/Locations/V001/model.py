from core import Supermodel
from core.util import Input, Output, Property
import json


# define the model class and inherit from class "Supermodel"
class Model(Supermodel):
    # model constructor
    def __init__(self, id, name: str):
        # instantiate supermodel
        super(Model, self).__init__(id, name)

        # define inputs
        #self.inputs['mode'] = Input(name='modus', unit='-', info="modus (live or simulation)")

        # define outputs
        self.outputs['distNets'] = Output(name='Distribution Networks', unit='Location: {Long, Lat}', info='???????')

        # define properties
        # - distribution network
        self.properties['distNets'] = Property("{}", str, name='distribution network', unit='-',
                                               info="distribution network with lon and lat",
                                               example='{"Baden": {"Lat": 45.255631, "Lon": 23.254853}, "Brugg": {...}, ...}')

        self.distNets = None


    async def func_birth(self):
        await self.func_amend(['distNets'])

    async def func_amend(self, keys=[]):
        if 'distNets' in keys:
            distNets = self.get_property('distNets')
            dict_distNets = json.loads(distNets)

            # formatting
            locations = list(dict_distNets.keys())
            list_lat = [dict_distNets[x]["Lat"] for x in locations]
            list_lon = [dict_distNets[x]["Lon"] for x in locations]

            # output
            output = {"dist_networks": locations, "Latitude": list_lat, "Longitude": list_lon}

            self.distNets = output

    async def func_peri(self, prep_to_peri=None):
        self.set_output('distNets', self.distNets)
