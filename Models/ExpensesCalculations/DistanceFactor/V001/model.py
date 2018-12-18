from pyjamas_core import Supermodel
from pyjamas_core.util import Input, Output, Property
from geopy.distance import geodesic
import numpy as np

# define the model class and inherit from class "Supermodel"
class Model(Supermodel):
    # model constructor
    def __init__(self, model_id, name: str):
        # instantiate supermodel
        super(Model, self).__init__(model_id, name)

        # define inputs
        self.inputs['KWData'] = Input(name='Power Plant', unit='-', info='European Power Plant')
        self.inputs['Locations'] = Input(name='Locations', unit='-', info='Locations with geographical coordinates')

        # define outputs
        self.outputs['DistanceFactor'] = Output(name='DistanceFactor', unit='[€/km*MWh]', info='Distance factor')

        # define properties
        self.properties['NetworkCost'] = Property(default=148E9, data_type=float, name='Network cost', unit='€',
                                           info="Network cost * annual amount of energy", example='148*10^9 € (Mittelspannung, Churwalden 2017)')

        # define persistent variables
        self.NetworkCost = None

    async def func_amend(self, keys=[]):
        if 'NetworkCost' in keys:
            self.NetworkCost = self.get_property('NetworkCost')

    async def func_peri(self, prep_to_peri=None):
        # inputs
        KW_data = await self.get_input('KWData')
        locations = await self.get_input('Locations')

        # calculate distance factor
        DistanceFactor = {'location': {}, 'dist_factor': {}}
        dist_factor = []

        # - loop over locations
        for it in range(0, len(locations['dist_networks'])):
            loc_lat_i = locations['Latitude'][it]
            loc_long_i = locations['Longitude'][it]

            # distance in meter between location of SPG and KW
            dist_KW = [geodesic((loc_lat_i, loc_long_i), (KW_data['lat'][jt], KW_data['long'][jt])).m for jt in range(0, len(KW_data['id']))]

            # distance times power of KW
            dist_power = np.array(dist_KW) * np.array(KW_data['p_inst'])
            dist_power_sum = np.sum(dist_power)
            # - annual (assume 8760 h = 1 year)
            dist_power_sum = dist_power_sum*8760

            # distance factor
            dist_factor_i = self.NetworkCost/dist_power_sum     # €/(m*W)
            # - change unit from €/(m*W) to €/(km*MWh)
            dist_factor_i = dist_factor_i*1E9
            # append in list
            dist_factor.append(dist_factor_i)


        # set output
        DistanceFactor['location'] = locations['dist_networks']
        DistanceFactor['dist_factor'] = dist_factor
        self.set_output("DistanceFactor", DistanceFactor)
