from core import Supermodel
from core.util import Input, Output, Property
import numpy as np
import geopy.distance  # geopy pakage installation required


# define the model class and inherit from class "Supermodel"
class Model(Supermodel):
    # model constructor
    def __init__(self, id, name: str):
        # instantiate supermodel
        super(Model, self).__init__(id, name)

        # define inputs
        self.inputs['Standorte'] = Input('SPGLocations', info='dict')
        self.inputs['KWDaten'] = Input('PowerPlantsData', info='dict')

        # define outputs
        self.outputs['Distanzkosten'] = Output('DistanceCost')

        self.DistanzFaktor = 0.1


    async def func_peri(self, prep_to_peri=None):
        # get inputs
        Standorte = await self.get_input('Standorte')
        KWDaten = await self.get_input('KWDaten')

        Distanzkosten = self.distancecost(Standorte, KWDaten)

        # set output
        self.set_output("Distanzkosten", Distanzkosten)


    # define additional methods (normal)
    # geopy pakage installation required to successfully compile and run this method
    def GeoDistanceVincenty(self, lat1, lon1, lat2, lon2):
        # coords_1 = (47.391377, 8.051434) # Aarau Bahnhof
        # coords_2 = (47.480756, 8.208632) # Brugg Bahnhof
        coords_1 = (lat1, lon1)
        coords_2 = (lat2, lon2)
        distance = geopy.distance.VincentyDistance(coords_1, coords_2).km
        # print ("Vincenty Distance:", distance,"km")
        return distance

    def distancecost(self, Standorte, KWDaten):
        # Determine the output power[W] of each power plant
        ###################################################################################################################
        # Input Arguments:
        # Standorte: Dictionary containing latitude and longitude coordinates of Signal price generator locations
        #            e.g. Baden, Brugg, olten, etc...
        #
        # KWDaten: Dictionary holding the different parameters of power plants
        # ------------------------------------------------------------------------------------
        #   id  fk_kwt   kw_bezeichnung    power[W]         spez_info             Capex   Opex
        # ------------------------------------------------------------------------------------
        #   1     2          WT            1000000       NH: 150,  Z0: 0.03         1     0.01
        #   2     1          PV            2000000       NH: 0,    Z0: {}           2     0.02
        #   3     2          WT            3000000       NH: 200,  Z0: 0.2          3     0.03
        #   4     1          PV            4000000       NH: 0,    Z0: {}           4     0.04
        #   5     2          WT            5000000       NH: 250,  Z0: 0.03         5     0.05
        #   6     1          PV            6000000       NH: 0,    Z0: {}           6     0.06
        #   8     3        OTHER           1000000       NH: 0,    Z0: {}           7     0.07
        #   10    3        OTHER           1000000       NH: 0,    Z0: {}           8     0.08
        #   11    4        OTHER           1000000       NH: 0,    Z0: {}           9     0.09
        # [KWID, FKKWT, KWBezeichnung, Power, Weitere spezifische parameter(Nabenhoehe, Z0, usw.), Capex, Opex, KEV, Brennstoffkosten, Entsorgungskostne, CO2-Kosten, usw.]
        #
        # Output Arguments:
        # Distanzkosten: Dictionary containing KWIDs in the first column  and corresponding calculated
        # marginal cost for a power plant in following 96 columns
        # -----------------
        # id   Grenzkosten   Note: Output matrix is sorted according to the incoming id's of KWDaten.
        # -----------------
        #  1    array(96)
        #  2    array(96)
        #  3    array(96)
        #  4    array(96)
        #  5    array(96)
        #  6    array(96)
        #  8    array(96)
        #  10   array(96)
        #  11   array(96)
        ###################################################################################################################
        SPGLocations = Standorte['dist_networks']

        dn_lon = Standorte['Longitude']
        dn_lat = Standorte['Latitude']

        KWLocationsLats = KWDaten['latitude']
        KWLocationsLons = KWDaten['longitude']

        kw_lat = KWDaten['latitude']
        kw_lon = KWDaten['longitude']



        d = [[self.GeoDistanceVincenty(kw_lat[i_kw], kw_lon[i_kw], dn_lat[i_dn], dn_lon[i_dn]) for i_dn in range(len(dn_lat))] for i_kw in range(len(kw_lat))]

        '''
        def CalculateDistanceOfAllPowerPlantsFromOneSPGLocation(SPGLocation):
            SPGLocationLat = Standorte[SPGLocation]['Lat']
            SPGLocationLon = Standorte[SPGLocation]['Lon']

            distance = [self.GeoDistanceVincenty(KWLat, KWLon, SPGLocationLat, SPGLocationLon) for KWLat, KWLon in zip(KWLocationsLats, KWLocationsLons)]
            DistanceCostsForOneSPGLocation = [(d*self.DistanzFaktor) for d in distance]
            return DistanceCostsForOneSPGLocation

        DistanceCostsForAllSPGLocation = [CalculateDistanceOfAllPowerPlantsFromOneSPGLocation(loc) for loc in SPGLocations]
        '''
        Distanzkosten = {'distribution_networks': Standorte['dist_networks'],
                         'power_plants': KWDaten['id'],
                         'costs': d}
        return Distanzkosten