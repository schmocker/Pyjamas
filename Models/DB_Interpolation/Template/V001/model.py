from core import Supermodel
from core.util import Input, Output, Property

# used for db querys
from Models.Technology.European_power_plant.V001.db import Base, Kraftwerk, Kraftwerkstyp, Brennstofftyp, \
    Brennstoffpreis, Verguetung, Entsorgungspreis, db_url
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker
import datetime, random

# used for interpolating
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d
from scipy.interpolate import griddata


# define the model class and inherit from class "Supermodel"
class Model(Supermodel):
    # model constructor
    def __init__(self, id, name: str):
        # instantiate supermodel
        super(Model, self).__init__(id, name)

        # define inputs
        self.inputs['t'] = Input({'name': 'time'})
        self.inputs['lat'] = Input({'name': 'latitude'})
        self.inputs['lon'] = Input({'name': 'longitude'})

        # define outputs
        self.outputs['kw_park'] = Output({'name': 'Kraftwerkspark'})

        # define properties
        self.properties['h_hub'] = Property(10, {'name': 'hub height'})
        self.properties['d'] = Property(10, {'name': 'diameter'})

        # define persistent variables
        self.pers_variable_0 = 5

    async def func_birth(self):

        if __name__ == "__main__":
            engine = create_engine(db_url)
            Base.metadata.bind = engine
            DBSession = sessionmaker(bind=engine)
            session = DBSession()

        return session

    async def func_prep(self):
        # calculate something
        prep_result = 3 * 5
        # pass values to peri function
        return prep_result

    async def func_peri(self, session, prep_to_peri=None):
        prep_result = prep_to_peri
        # get inputs
        in1 = await self.get_input('t')
        in2 = await self.get_input('lat')
        in3 = await self.get_input('lon')

        t = session.query(Kraftwerk).first()
        lat = session.query(Kraftwerk).all()

        # TODO Zeit muss noch skaliert werden, zB in Sekunden absolut(?).
        # TODO Sonst ist Interpolation über Mitternacht nicht möglich.

        break1 = 0

        # calculate something
        # One can declare custom functions (eg: see end of file)
        # If you declare them "async" you will have to "await" them (like "extremely_complex_calculation")
        # Else one could declare "normal" (blocking) functions as well (like "complex_calculation")
        out1 = prep_result * self.complex_calculation(in1)
        out2 = await self.extremely_complex_calculation(in1, in2)

        # set output
        self.set_output("p_el", out1)
        self.set_output("f_rot", out2)

        # pass values to post function
        outputs = {'out1': out1, 'out2': out2}
        return outputs

    async def func_post(self, peri_to_post=None):
        outputs = peri_to_post
        # do something with the values (eg: overwrite persistent variable)
        self.pers_variable_0 = outputs['out1']

    async def func_death(self):
        print("I am dying! Bye bye!")

    # define additional methods (normal)
    def interpol(self, t, lat, lon):
        rand_data = True
        rand_test = True
        plot_date = True
        """
        INPUTS:
            lat: Latitude [decimal degrees, (45,3452)]; ndarray, nx1, float
            lon: Longitude [decimal degrees, (45,3452)]; ndarray, nx1, float
            time: Time [decimal hours (12,25)]; mx1, float
            values: Temperatur or ...; ndarray, mxn, float
            xi:  
        """
        # TODO Ausrichtung der Input Arrays kontrollieren (Zeile/Spalte)

        if rand_data:
            # # set random weather station locations
            # lat = np.random.rand(10)  # * 30 + 20
            # lon = np.random.rand(10)  # * 20 - 5
            # time = np.r_[0:24:3]
            # values = np.random.rand(lat.size, time.size)

            # set fixed weather station locations
            lat = np.array([0, 0, 0, .5, .5, .5, 1, 1, 1])
            lon = np.array([0, .5, 1, 0, .5, 1, 0, .5, 1])
            time = np.r_[0:24:6]
            values = np.array([[10, 10, 10],
                               [20, 20, 20],
                               [30, 30, 30],
                               [40, 40, 40],
                               [50, 50, 50],
                               [60, 60, 60],
                               [70, 70, 70],
                               [80, 80, 80],
                               [90, 90, 90],
                               [100, 100, 100],
                               [110, 110, 110],
                               [120, 120, 120]])

        else:
            lat = lat
            lon = lon

        if rand_test:
            xi = np.array([[.25, .5, .75, .25],  # testpoints 3D
                       [.25, .5, 1, .5],
                       [3, 12, 15, 24]])

        else:
            lat=lat
            lon=lon


        # arrange inputs for griddata
        gridpoints = np.vstack((np.tile(lat, time.size), np.tile(lon, time.size), np.repeat(time, lat.size)))
        latgrid = gridpoints[0, :]
        longrid = gridpoints[1, :]
        timegrid = gridpoints[2, :]

        values = values.reshape(-1)

        # interpolate
        interp_nearest = griddata(gridpoints.T, values.T, xi.T, method='nearest')
        interp_linear = griddata(gridpoints.T, values.T, xi.T, method='linear')

        # replace linear NAN with nearest
        interp_combined = np.where(np.isnan(interp_linear), interp_nearest, interp_linear)

        print('interp_linear')
        print(interp_linear)
        print('interp_nearest')
        print(interp_nearest)
        print('interp_combined')
        print(interp_combined)

        if plot_data:

            ax1 = plt.subplot(221, projection='3d')
            ax1.scatter(latgrid, longrid, timegrid, c=values, depthshade=False)
            ax1.scatter(xi[0, :], xi[1, :], xi[2, :], c='r', depthshade=False)
            ax1.set_xlim3d(0, 1)
            ax1.set_ylim3d(0, 1)
            ax1.set_zlim3d(0, 24)
            ax1.set_xlabel("lat")
            ax1.set_ylabel("lon")
            ax1.set_zlabel("time")

            ax2 = plt.subplot(222)
            ax2.plot(lat, lon, 'k.', ms=5)
            ax2.plot(xi[0, :], xi[1, :], 'ro')
            plt.title('Lat/Lon')
            ax2.set_xlim(-.1, 1.1)
            ax2.set_ylim(-.1, 1.1)
            ax2.set_xlabel("lat")
            ax2.set_ylabel("lon")

            ax3 = plt.subplot(223)
            ax3.plot(xi[0, :], xi[2, :], 'ro')
            plt.title('Lat/Time')
            ax3.set_xlim(-.1, 1.1)
            ax3.set_ylim(-.1, 25)
            ax3.set_xlabel("lat")
            ax3.set_ylabel("time")

            ax4 = plt.subplot(224)
            ax4.plot(xi[1, :], xi[2, :], 'ro')
            plt.title('Lon/Time')
            ax4.set_xlim(-.1, 1.1)
            ax4.set_ylim(-.1, 25)
            ax4.set_xlabel("lon")
            ax4.set_ylabel("time")

            plt.show()

    return speed_cut

    # define additional methods (async)
    async def extremely_complex_calculation(self, speed, time):
        distance = speed * time / self.get_property("h_hub")
        return distance



