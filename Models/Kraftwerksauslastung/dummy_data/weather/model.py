from core import Supermodel
from core.util import Input, Output, Property
import numpy as np


# define the model class and inherit from class "Supermodel"
class Model(Supermodel):
    # model constructor
    def __init__(self, id, name: str):
        # instantiate supermodel
        super(Model, self).__init__(id, name)
        # define outputs
        self.outputs['weather'] = Output('WeatherData')


        # define persistent variables
        self.weather = None

    async def func_birth(self):
        # Temporary dummy data for testing purpose, Will be replaced by the data coming from the database
        # WeatherData: Dictionary holding Power plant IDs(KWIDs) and weather data for all types of power plants
        # ----------------------------------------------
        #  id      windspeed   radiation   windmesshoehe
        # ----------------------------------------------
        #  1(WT)   array(96)   None            50
        #  2(PV)   None        array(96)       None
        #  3(WT)   array(96)   None            45
        #  4(PV)   None        array(96)       None
        #  5(WT)   array(96)   None            80
        #  6(PV)   None        array(96)       None
        #  8       None        None            None
        #  10      None        None            None
        #  11      None        None            None

        ws1=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32
            ,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32
            ,25,56,7,8,96,10,10,20,23,24,25,56,7,8,96,10,10,20,23,24,25,56,7,8,96,10,10,20,23,24,25,56]
        ra2=[0.00000,0.00000,0.00000,0.00000,0.00000,0.0000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000
            ,0.00000,0.00000,0.00000,0.00000,0.00000,0.0000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000
            ,2.06780,4.54916,30.1898,47.5594,104.630,153.430,202.23,257.234,228.285,365.587,411.905,465.255
            ,517.363,562.028,604.211,653.838,715.872,737.377,770.875,813.058,836.631,862.272,873.438,899.493
            ,915.208,923.065,931.750,923.065,916.035,914.794,897.011,877.987,834.150,826.292,819.262,791.553
            ,657.146,726.624,636.055,528.116,603.384,546.312,511.160,468.977,417.282,366.000,312.651,262.610
            ,219.186,176.176,135.647,93.8781,64.5153,43.4238,38.0475,26.0542,14.4746,10.3390,4.13560,2.89492
            ,0.00000,0.00000,0.00000,0.00000,0.00000,0.0000,0.000000,0.00000,0.00000,0.00000,0.00000,0.00000]
        ws3=[30,11,2,3,4,5,6,7,8,96,20,11,2,3,4,5,6,7,8,96,20,11,2,3,4,5,6,7,8,96,20,11
            ,2,3,4,5,6,7,8,96,20,11,2,3,4,5,6,7,8,96,20,11,2,3,4,5,6,7,8,96,20,11,2,3
            ,4,5,6,7,8,96,20,11,2,3,4,5,6,7,8,96,20,11,2,3,4,5,6,7,8,96,20,11,2,3,4,5]
        ra4=[0.00000,0.00000,0.00000,0.00000,0.00000,0.0000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000
            ,0.00000,0.00000,0.00000,0.00000,0.00000,0.0000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000
            ,2.06780,4.54916,30.1898,47.5594,104.630,153.430,202.23,257.234,228.285,365.587,411.905,465.255
            ,517.363,562.028,604.211,653.838,715.872,737.377,770.875,813.058,836.631,862.272,873.438,899.493
            ,915.208,923.065,931.750,923.065,916.035,914.794,897.011,877.987,834.150,826.292,819.262,791.553
            ,657.146,726.624,636.055,528.116,603.384,546.312,511.160,468.977,417.282,366.000,312.651,262.610
            ,219.186,176.176,135.647,93.8781,64.5153,43.4238,38.0475,26.0542,14.4746,10.3390,4.13560,2.89492
            ,0.00000,0.00000,0.00000,0.00000,0.00000,0.0000,0.000000,0.00000,0.00000,0.00000,0.00000,0.00000]
        ws5=[50,11,2,3,4,5,6,7,8,96,50,11,2,3,4,5,6,7,8,96,50,11,2,3,4,5,6,7,8,96,50,11
            ,2,3,4,5,6,7,8,96,50,11,2,3,4,5,6,7,8,96,50,11,2,3,4,5,6,7,8,96,50,11,2,3
            ,4,5,6,7,8,96,50,11,2,3,4,5,6,7,8,96,50,11,2,3,4,5,6,7,8,96,50,11,2,3,4,5]
        ra6=[0.00000,0.00000,0.00000,0.00000,0.00000,0.0000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000
            ,0.00000,0.00000,0.00000,0.00000,0.00000,0.0000,0.00000,0.00000,0.00000,0.00000,0.00000,0.00000
            ,2.06780,4.54916,30.1898,47.5594,104.630,153.430,202.23,257.234,228.285,365.587,411.905,465.255
            ,517.363,562.028,604.211,653.838,715.872,737.377,770.875,813.058,836.631,862.272,873.438,899.493
            ,915.208,923.065,931.750,923.065,916.035,914.794,897.011,877.987,834.150,826.292,819.262,791.553
            ,657.146,726.624,636.055,528.116,603.384,546.312,511.160,468.977,417.282,366.000,312.651,262.610
            ,219.186,176.176,135.647,93.8781,64.5153,43.4238,38.0475,26.0542,14.4746,10.3390,4.13560,2.89492
            ,0.00000,0.00000,0.00000,0.00000,0.00000,0.0000,0.000000,0.00000,0.00000,0.00000,0.00000,0.00000]

        self.WeatherData = {'id': [1, 2, 3, 4, 5, 6, 8 ,10 ,11],
                            'windspeed': [ws1, None, ws3, None, ws5, None, None, None, None],
                            'radiation': [None, ra2, None, ra4, None, ra6, None, None, None],
                            'windmesshoehe': [50, None, 45, None, 80, None, None, None, None]}


    async def func_peri(self, prep_to_peri=None):

        # set output
        self.set_output("weather", self.WeatherData)





