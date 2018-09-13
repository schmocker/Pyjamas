from core import Supermodel
from core.util import Input, Output, Property
import geopy.distance


# define the model class and inherit from class "Supermodel"
class Model(Supermodel):
    # model constructor
    def __init__(self, model_id, name: str):
        # instantiate supermodel
        super(Model, self).__init__(model_id, name)

        # define inputs
        self.inputs['Standorte'] = Input('SPGLocations',
                                         info='dict containing location names and coordinates [lat/lon] of SPGs')
        self.inputs['KWDaten'] = Input('PowerPlantsData',
                                       info='dict containing power plant information, including coordinates')

        # define outputs
        self.outputs['Distanzkosten'] = Output('DistanceCost', unit='[€/m*J]')

        # define properties
        self.properties['dis_factor'] = Property('DistanceFactor', default=0.021, data_type=float, unit='[€/km*MWh]')

        self.DistanzFaktor = None

    async def func_amend(self, keys=[]):
        if 'dis_factor' in keys:
            self.DistanzFaktor = self.get_property('dis_factor') / 3.6e12  # [€/km*MWh] to [€/m*J] (SI Units)

    async def func_peri(self, prep_to_peri=None):
        # get inputs
        standorte = await self.get_input('Standorte')
        kw_daten = await self.get_input('KWDaten')

        distanzkosten = self.distancecost(standorte, kw_daten)

        # set output
        self.set_output("Distanzkosten", distanzkosten)

    def distancecost(self, standorte, kw_daten):
        # Determine the distance cost[$/m*J] of each power plant
        ################################################################################################################
        # Input Arguments:
        # Standorte: Dictionary containing latitude and longitude coordinates of Signal price generator locations
        #            e.g. Baden, Brugg, olten, etc...
        #
        # KWDaten: Dictionary holding the different parameters of power plants
        #
        # Output Arguments:
        # Distanzkosten: Dictionary containing the locations of all Signal Price Generators (SPGs), power plant ids and
        # distance costs for all SPG locations (calculated using the distance between SPG locations and power plant
        # locations)
        # -----------------------------------
        # SPG-locations     id      costs
        # -----------------------------------
        #     Baden         1     cost matrix
        #     Brugg         2                   PP1        PP2       ...       PPn
        #     Olten         3     Standort1   c[€/m*J]   c[€/m*J]    ...    c[€/m*J]
        #                   .     Standort2   c[€/m*J]   c[€/m*J]    ...    c[€/m*J]
        #                   .     Standort3   c[€/m*J]   c[€/m*J]    ...    c[€/m*J]
        #                   n
        ################################################################################################################

        dn_lat = standorte['Latitude']
        dn_lon = standorte['Longitude']

        kw_lat = kw_daten['lat']
        kw_lon = kw_daten['long']

        # Distance costs for all SPG locations
        costs = [[self.DistanzFaktor *
                  geopy.distance.VincentyDistance((kw_lat[i_kw], kw_lon[i_kw]), (dn_lat[i_dn], dn_lon[i_dn])).m
                  for i_dn in range(len(dn_lat))] for i_kw in range(len(kw_lat))]

        distanzkosten = {'distribution_networks': standorte['dist_networks'],
                         'power_plants': kw_daten['id'],
                         'costs': costs}
        return distanzkosten
