from core import Supermodel
from core.util import Input, Output, Property
import geopy.distance  # geopy pakage installation required


# define the model class and inherit from class "Supermodel"
class Model(Supermodel):
    # model constructor
    def __init__(self, id, name: str):
        # instantiate supermodel
        super(Model, self).__init__(id, name)

        # define inputs
        self.inputs['Standorte'] = Input('SPGLocations', info='geographical coordinates[lat/lon] of SPGs required')
        self.inputs['KWDaten'] = Input('PowerPlantsData',info='dict, geographical coordinates[lat/lon] of power plants required')

        # define outputs
        self.outputs['Distanzkosten'] = Output('DistanceCost', unit='[€/J]')

        # define properties
        self.properties['dis_factor'] = Property('DistanceFactor', default=0.01, data_type=float, unit='[€/m*J]')

        self.DistanzFaktor = 0.1



    async def func_amend(self, keys=[]):
        if 'dis_factor' in keys:
            self.DistanzFaktor = self.get_property('dis_factor')

    async def func_peri(self, prep_to_peri=None):
        # get inputs
        Standorte = await self.get_input('Standorte')
        KWDaten = await self.get_input('KWDaten')

        Distanzkosten = self.distancecost(Standorte, KWDaten)

        # set output
        self.set_output("Distanzkosten", Distanzkosten)


    # define additional methods (normal)
    def GeoDistanceVincenty(self, lat1, lon1, lat2, lon2):
        # Determine the distance[m] between two coordinates
        # coords_1 = (47.391377, 8.051434) # Aarau Bahnhof
        # coords_2 = (47.480756, 8.208632) # Brugg Bahnhof
        coords_1 = (lat1, lon1)
        coords_2 = (lat2, lon2)
        distance = geopy.distance.VincentyDistance(coords_1, coords_2).km
        distance = distance*1000  # km to m conversion
        return distance

    def distancecost(self, Standorte, KWDaten):
        # Determine the distance cost[€/J] of each power plant
        ################################################################################################################
        # Input Arguments:
        # Standorte: Dictionary containing latitude and longitude coordinates of Signal price generator locations
        #            e.g. Baden, Brugg, olten, etc...
        #
        # KWDaten: Dictionary holding the different parameters of power plants
        # ----------------------------------------------------------------------------------------------
        #   id  fk_kwt   kw_bezeichnung    power[W]          spez_info             Capex   Opex,  usw...
        # ----------------------------------------------------------------------------------------------
        #   1     2       Windturbine      1000000       NH: 150,  Z0: 0.03          1     0.01
        #   2     1      Photovoltaik      2000000       NH: 0,    Z0: {}            2     0.02
        #   3     2       Windturbine      3000000       NH: 200,  Z0: 0.2           3     0.03
        #   4     1      Photovoltaik      4000000       NH: 0,    Z0: {}            4     0.04
        #   5     2       Windturbine      5000000       NH: 250,  Z0: 0.03          5     0.05
        #   6     1      Photovoltaik      6000000       NH: 0,    Z0: {}            6     0.06
        #   8     3        Others          1000000       NH: 0,    Z0: {}            7     0.07
        #   10    3        Others          1000000       NH: 0,    Z0: {}            8     0.08
        #   11    4        Others          1000000       NH: 0,    Z0: {}            9     0.09
        # [KWID, FKKWT, KWBezeichnung, Power, Weitere spezifische parameter(Nabenhoehe, Z0, usw.), Capex,
        #  Opex, KEV, Brennstoffkosten, Entsorgungskostne, CO2-Kosten, usw.]
        #
        # Output Arguments:
        # Distanzkosten: Dictionary containing the locations of all Signal Price Generators (SPGs), power plant ids and
        # distance costs for all SPG locations (calculated using the distance between SPG locations and power plant
        # locations)
        # -----------------------------------
        # SPG-locations     id      costs
        # -----------------------------------
        #     Baden         1     cost matrix
        #     Brugg         2                   PP1      PP2     PP3      PP4      PP5      PP6      PP7      PP8    ...
        #     Olten         3     Standort1   c[€/J]   c[€/J]   c[€/J]   c[€/J]   c[€/J]   c[€/J]   c[€/J]   c[€/J]
        #                   4     Standort2   c[€/J]   c[€/J]   c[€/J]   c[€/J]   c[€/J]   c[€/J]   c[€/J]   c[€/J]
        #                   5     Standort3   c[€/J]   c[€/J]   c[€/J]   c[€/J]   c[€/J]   c[€/J]   c[€/J]   c[€/J]
        #                   .
        #                   .
        #                   .
        #                   14
        ################################################################################################################
        SPGLocations = Standorte['dist_networks']

        dn_lon = Standorte['Longitude']
        dn_lat = Standorte['Latitude']

        kw_lat = KWDaten['lat']
        kw_lon = KWDaten['long']

        # Distance costs for all SPG locations
        costs = [[self.DistanzFaktor * self.GeoDistanceVincenty(kw_lat[i_kw], kw_lon[i_kw], dn_lat[i_dn], dn_lon[i_dn]) for i_dn in range(len(dn_lat))] for i_kw in range(len(kw_lat))]

        Distanzkosten = {'distribution_networks': Standorte['dist_networks'],
                         'power_plants': KWDaten['id'],
                         'costs': costs}
        return Distanzkosten