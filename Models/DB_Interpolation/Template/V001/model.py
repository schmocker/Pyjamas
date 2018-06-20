# imports for core
from numpy.lib.tests.test__datasource import valid_baseurl

from core import Supermodel
from core.util import Input, Output, Property



# imports for db querys
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker
import os
from Models.Technology.European_power_plant.V001.db import Base, Kraftwerk, Kraftwerkstyp, Brennstofftyp, \
    Kraftwerksleistung, Brennstoffpreis, Verguetung, Entsorgungspreis, Co2Preis, create_dummy_data


import datetime, random

# used for interpolating
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d
from scipy.interpolate import griddata


# define the model class and inherit from class "Supermodel"
class Model(Supermodel):
    # model constructor
    def __init__(self, model_id, name: str):
        # instantiate supermodel
        super(Model, self).__init__(model_id, name)

        # define inputs
        self.inputs['t'] = Input({'name': 'Zeitarray'})

        # define outputs
        self.outputs['kw_park'] = Output({'name': 'Kraftwerkspark'})

        # define properties
        # Property(<initial value>,<type>,<info dictionary>)
        self.properties['prop1'] = Property(10, float, {'name': 'property1'})

        # define persistent variables
        self.pers_variable_0 = 5
        self.session = None

    async def func_birth(self):
        # create DBsession
        engine = create_engine(db_url)
        Base.metadata.bind = engine
        DBSession = sessionmaker(bind=engine)
        self.session = DBSession()

    async def func_amend(self, keys=[]):
        pass

    async def func_prep(self):
        pass
        ## # calculate something
        ## prep_result = 3 * 5
        ## # pass values to peri function
        ## return prep_result

    async def func_peri(self, prep_to_peri=None):
        ## prep_result = prep_to_peri

        # get inputs
        t_arr = await self.get_input('t')
        # only first time value
        t = t_arr[0]

        # query Kraftwerk
        db_kw = self.session.query(Kraftwerk).all()
        db_kw_id = self.session.query(Kraftwerk.id).order_by(Kraftwerk.id).all()
        db_kw_bez = self.session.query(Kraftwerk.bezeichnung).order_by(Kraftwerk.id).all()
        db_kw_fk_kwt = self.session.query(Kraftwerk.fk_kraftwerkstyp).order_by(Kraftwerk.id).all()
        db_kw_long = self.session.query(Kraftwerk.long).order_by(Kraftwerk.id).all()
        db_kw_lat = self.session.query(Kraftwerk.lat).order_by(Kraftwerk.id).all()
        db_kw_pinst = self.session.query(Kraftwerk.power_inst).order_by(Kraftwerk.id).all()
        db_kw_datetime = self.session.query(Kraftwerk.datetime).order_by(Kraftwerk.id).all()
        db_kw_spezinfo = self.session.query(Kraftwerk.spez_info).order_by(Kraftwerk.id).all()

        # query Brennstoffpreis
        db_bsp = self.session.query(Brennstoffpreis).all()

        # query Brennstofftyp
        db_bst = self.session.query(Brennstofftyp).all()

        # query Co2Preis
        db_co2 = self.session.query(Co2Preis).all()

        # query Entsorgungspreis
        db_ents = self.session.query(Entsorgungspreis).all()

        # query Kraftwerkstyp
        db_kwt = self.session.query(Kraftwerkstyp).all()

        # query Vergütung
        db_verg = self.session.query(Verguetung).all()

        # alternative
        # db_kw_id = [i.id for i in db_kw]
        # db_kw_bez = [i.bezeichnung for i in db_kw]
        # db_kw_fk_kwt = [i.fk_kraftwerkstyp for i in db_kw]
        # db_kw_long = [i.long for i in db_kw]
        # db_kw_lat = [i.lat for i in db_kw]
        # db_kw_pinst = [i.power_inst for i in db_kw]
        # db_kw_datetime = [i.datetime for i in db_kw]
        # db_kw_spezinfo = [i.spez_info for i in db_kw]

        break1 = 0

        # calculate something
        # One can declare custom functions (eg: see end of file)
        # If you declare them "async" you will have to "await" them (like "extremely_complex_calculation")
        # Else one could declare "normal" (blocking) functions as well (like "complex_calculation")

        # KEV Interpolation
          # get KW_id ---> KWT
        kev = self.interpol_3d(db_kev_t, db_kev_lat, db_kev_long, db_kev_preis, db_kw_lat, db_kw_long, t)

        # P_inst Interpolation
        pinst = self.interpol_1d(db_kw_pinst, ..., t)

        # Brennstoffpreis Interpolation
          # get KW_id--> KWT-->BST
        bsp = self.interpol_3d(db_bsp_t, db_bsp_lat, db_bsp_long, db_bsp_preis, db_kw_lat, db_kw_long, t)

        # CO2-Preise Interpolation
        co2 = self.interpol_3d(db_co2_t, db_co2_lat, db_co2_long, db_co2_preis, db_kw_lat, db_kw_long, t)

        # Entsorgungskosten Interpolation
          # get KW_id ---> KWT
        ents = self.interpol_3d(db_ents_t, db_ents_lat, db_ents_long, db_ents_preis, db_kw_lat, db_kw_long, t)




        # TODO assemble kwp table

        # set output
        self.set_output("kw_park", kwp)

        # pass values to post function
        outputs = {'kw_park': kwp}
        return outputs

    async def func_post(self, peri_to_post=None):
        pass
        # outputs = peri_to_post
        # # do something with the values (eg: overwrite persistent variable)
        # self.pers_variable_0 = outputs['out1']

    async def func_death(self):
        pass

    # 3D Interpolation
    def interpol_3d(self, time, lat, long, values, kw_lat, kw_long, kw_t):
        test_data = True
        rand_test = True
        plot_data = True
        """
        INPUTS:
            lat: Latitude [decimal degrees, (45,3452)]; ndarray, nx1, float
            long: Longitude [decimal degrees, (45,3452)]; ndarray, nx1, float
            time: Time [datetime]; mx1, float
            values: Temperatur or ...; ndarray, mxn, float
            xi:  
        """
        # TODO Ausrichtung der Input Arrays kontrollieren (Zeile/Spalte)

        if test_data:
            # # set random weather station locations
            # lat = np.random.rand(10)  # * 30 + 20
            # long = np.random.rand(10)  # * 20 - 5
            # time = np.r_[0:24:3]
            # values = np.random.rand(lat.size, time.size)

            # set fixed weather station locations
            lat = np.array([0, 0, 0, .5, .5, .5, 1, 1, 1])
            long = np.array([0, .5, 1, 0, .5, 1, 0, .5, 1])
            #time = np.r_[0:24:6]
            t0 = datetime.datetime.now()
            time = t0 + np.arange(96) * datetime.timedelta(seconds=900)

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
            long = long
            time = time
            values = values

        if rand_test:
            xi = np.array([[.25, .5, .75, .25],  # testpoints 3D
                       [.25, .5, 1, .5],
                       [3, 12, 15, 24]])

        else:

            kw_lat = kw_lat
            kw_long = kw_long
            kw_t = kw_t
            xi = np.vstack((kw_lat,kw_long,kw_t))

        # arrange inputs for griddata
        gridpoints = np.vstack((np.tile(lat, time.size), np.tile(long, time.size), np.repeat(time, lat.size)))
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
            ax1.set_xlabel("lat")
            ax1.set_ylabel("lon")
            ax1.set_zlabel("time")

            ax2 = plt.subplot(222)
            ax2.plot(lat, long, 'k.', ms=5)
            ax2.plot(xi[0, :], xi[1, :], 'ro')
            plt.title('Lat/Lon')
            ax2.set_xlabel("lat")
            ax2.set_ylabel("lon")

            ax3 = plt.subplot(223)
            ax3.plot(xi[0, :], xi[2, :], 'ro')
            plt.title('Lat/Value')
            ax3.set_xlabel("lat")
            ax3.set_ylabel("Value")

            ax4 = plt.subplot(224)
            ax4.plot(xi[1, :], xi[2, :], 'ro')
            plt.title('Lon/Value')
            ax4.set_xlabel("lon")
            ax4.set_ylabel("Value")

            plt.show()

        return interp_combined

    # 1D Interpolation
    def interpol_1d(self, time, values, kw_t):
        test_data = True
        rand_test = True
        plot_data = True
        """
        INPUTS:
            time: Time [datetime]; nx1
            values: Temperatur or ...; ndarray, nx1, float
            kw_t:   
        """
        # TODO Ausrichtung der Input Arrays kontrollieren (Zeile/Spalte)

        if test_data:
            # # set random weather station locations
            # time = np.r_[0:24:3]
            # values = np.random.rand(10)

            # set fixed weather station locations
            #time = np.r_[0:24:6]
            t0 = datetime.datetime.now()
            time = t0 + np.arange(96) * datetime.timedelta(seconds=900)

            values = np.array([10, 20, 40, 50, 70, 80, 100, 90, 60, 30])

        else:
            time = time
            values = values

        if rand_test:
            xi = np.array([.25, .5, .75, .25])  # testpoints 1D

        else:
            xi = kw_t


        # interpolate
        interp_nearest = griddata(time.T, values.T, xi.T, method='nearest')
        interp_linear = griddata(time.T, values.T, xi.T, method='linear')

        # replace linear NAN with nearest
        interp_combined = np.where(np.isnan(interp_linear), interp_nearest, interp_linear)

        print('interp_linear')
        print(interp_linear)
        print('interp_nearest')
        print(interp_nearest)
        print('interp_combined')
        print(interp_combined)

        if plot_data:

            ax1 = plt.subplot(121)
            ax1.plot(time, values, 'k.', ms=5)
            ax1.plot(xi, interp_combined, 'ro')
            plt.title('Result')
            ax1.set_xlabel("time")
            ax1.set_ylabel("values")

            plt.show()

        return interp_combined

    # define additional methods (async)
    async def extremely_complex_calculation(self, speed, time):
        distance = speed * time / self.get_property("prop1")
        return distance


def start_db():
    db_path = 'db/powerplants.db'
    if not os.path.isfile(db_path):
        open(db_path, 'a').close()

    # an engine is the real DB
    engine = create_engine('sqlite:///'+db_path)

    # delete all tables
    Base.metadata.drop_all(engine)

    # create all tables
    Base.metadata.create_all(engine)

    # a session is used to communicate with the DB
    Base.metadata.bind = engine
    session = sessionmaker(bind=engine)()

    # create dummy data
    create_dummy_data(session)

    return session


if __name__ == "__main__":
    db = start_db()

    kw = db.query(Kraftwerk).first()

    r = 5


if __name__ == "__main__":
    dt = 900
    t0 = datetime.datetime.now()
    t = t0 + np.arange(96) * datetime.timedelta(seconds=dt)
    inputs = {'t': t}

    h_hub = 12
    d = 26
    properties = {'h_hub': h_hub, 'd': d}

    outputs = Model.test(inputs, properties)

