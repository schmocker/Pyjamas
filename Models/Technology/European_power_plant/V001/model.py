# imports for core
from numpy.lib.tests.test__datasource import valid_baseurl
from core import Supermodel
from core.util import Input, Output, Property

# imports for database
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker
import os
from Models.Technology.European_power_plant.V001.db import Base, Kraftwerk, Kraftwerkstyp, Brennstofftyp, \
    Kraftwerksleistung, Brennstoffpreis, Verguetung, Entsorgungspreis, Co2Preis, create_dummy_data

# general imports
import datetime
import random
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d # is used even if warning says otherwise!
from scipy.interpolate import griddata
from pytz import timezone

from Models._utils.time import utc_time2datetime
from Models._utils.time import datetime2utc_time

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
        self.db = None

    async def func_birth(self):
        # create database
        self.db = start_db()

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
        t_in = await self.get_input('t')
        # only first time value for interpolation
        kw_time = t_in[0]


        # TODO query all data
        # query Kraftwerk
        db_kw = self.db.query(Kraftwerk).all()
        db_kw_id = self.db.query(Kraftwerk.id).order_by(Kraftwerk.id).all()
        db_kw_bez = self.db.query(Kraftwerk.bezeichnung).order_by(Kraftwerk.id).all()
        db_kw_fk_kwt = self.db.query(Kraftwerk.fk_kraftwerkstyp).order_by(Kraftwerk.id).all()
        db_kw_long = self.db.query(Kraftwerk.long).order_by(Kraftwerk.id).all()
        db_kw_lat = self.db.query(Kraftwerk.lat).order_by(Kraftwerk.id).all()

        # alternative
        # db_kw_id = [i.id for i in db_kw]
        # db_kw_bez = [i.bezeichnung for i in db_kw]
        # db_kw_fk_kwt = [i.fk_kraftwerkstyp for i in db_kw]
        # db_kw_long = [i.long for i in db_kw]
        # db_kw_lat = [i.lat for i in db_kw]

        # query Kraftwerksleistung
        db_kwl = self.db.query(Kraftwerksleistung).order_by(Kraftwerksleistung.id).all()
        db_kwl_id = self.db.query(Kraftwerksleistung.id).order_by(Kraftwerksleistung.id).all()
        db_kwl_fk_kw = self.db.query(Kraftwerksleistung.fk_kraftwerk).order_by(Kraftwerksleistung.id).all()
        db_kwl_pinst = self.db.query(Kraftwerksleistung.power_inst).order_by(Kraftwerksleistung.id).all()
        db_kwl_datetime = self.db.query(Kraftwerksleistung.datetime).order_by(Kraftwerksleistung.id).all()

        # query Brennstoffpreis
        db_bsp = self.db.query(Brennstoffpreis).all()

        # query Brennstofftyp
        db_bst = self.db.query(Brennstofftyp).all()

        # query Co2Preis
        db_co2 = self.db.query(Co2Preis).all()

        # query Entsorgungspreis
        db_ents = self.db.query(Entsorgungspreis).order_by(Entsorgungspreis.id).all()
        db_ents_id = self.db.query(Entsorgungspreis.id).order_by(Entsorgungspreis.id).all()
        db_ents_fk_kwt = self.db.query(Entsorgungspreis.fk_kraftwerkstyp).order_by(Entsorgungspreis.id).all()
        db_ents_long = self.db.query(Entsorgungspreis.long).order_by(Entsorgungspreis.id).all()
        db_ents_lat = self.db.query(Entsorgungspreis.lat).order_by(Entsorgungspreis.id).all()
        db_ents_datetime = self.db.query(Entsorgungspreis.datetime).order_by(Entsorgungspreis.id).all()
        db_ents_preis = self.db.query(Entsorgungspreis.preis).order_by(Entsorgungspreis.id).all()

        # query Kraftwerksleistung
        db_kwt = self.db.query(Kraftwerksleistung).all()

        # query Kraftwerkstyp
        db_kwt = self.db.query(Kraftwerkstyp).all()

        # query Vergütung
        db_verg = self.db.query(Verguetung).all()


        # TODO Interpolationen fertig, outputs ordnen
        # KEV Interpolation
          # get KW_id ---> KWT
        kev = self.interpol_3d(db_kev_t, db_kev_lat, db_kev_long, db_kev_preis, db_kw_lat, db_kw_long, kw_time)

        # P_inst Interpolation
        pinst = self.interpol_1d(db_time, db_values, kw_time)

        # Brennstoffpreis Interpolation
          # get KW_id--> KWT-->BST
        bsp = self.interpol_3d(db_bsp_t, db_bsp_lat, db_bsp_long, db_bsp_preis, db_kw_lat, db_kw_long, kw_time)

        # CO2-Preise Interpolation
        co2 = self.interpol_3d(db_co2_t, db_co2_lat, db_co2_long, db_co2_preis, db_kw_lat, db_kw_long, kw_time)

        # Entsorgungspreis Interpolation
          # get KW_id ---> KWT
        ents = self.interpol_3d(db_ents_t, db_ents_lat, db_ents_long, db_ents_preis, db_kw_lat, db_kw_long, kw_time)

        # Verguetung Interpolation
          # get KW_id ---> KWT

        verg = []
        for kw in db_kw:
            print("Verguetung", kw.id, kw.bezeichnung)
            db_verg = kw.kraftwerkstyp.verguetungen
            db_verg_t = [i.datetime for i in db_verg]
            db_verg_lat = [i.lat for i in db_verg]
            db_verg_long = [i.long for i in db_verg]
            db_verg_beitrag = [i.beitrag for i in db_verg]

            db_kw_lat = kw.lat
            db_kw_long = kw.long

            verg = verg + [self.interpol_3d(db_verg_t, db_verg_lat, db_verg_long, db_verg_beitrag, db_kw_lat, db_kw_long, kw_time)]
        verg = np.array(verg)



        # TODO Berechnugnen integrieren für
        # TODO CO2-Kosten (CO2Preise*CO2_Emiss Fakt/Wirkungsgrad)
        # TODO Entsorgungskosten (entsorgungskosten/Wirkungsgrad)
        # TODO Brennstoffkosten (Brennstoffpreise/Wirkungsgrad)

        # TODO assemble kwp table
        # id¦bez¦lat¦long¦p_inst¦fk_KWT¦bez_KWT¦bez_subtyp¦wirk.¦spez_opex¦capex¦p_typ¦spez_info¦ents.preis¦verg¦
        # fk_bst¦bez_bst¦co2emissfakt¦bs_preis¦co2_preis¦co2kosten¦entskosten¦brennstoffkosten
        # set output
        self.set_output("kw_park", kwp)

        # TODO remove if func_post is unused
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

    # TODO Ausrichtung der Input Arrays kontrollieren (Zeile/Spalte)
    # 3D Interpolation
    def interpol_3d(self, db_time, db_lat, db_long, db_values, kw_lat, kw_long, kw_time):
        test_data = True
        test_data_ordered = True
        plot_data = True

        """
        This function interpolates in a grid of points (db_lat,db_long,db_time) with assigned values (db_values).
        It interpolates for points given by (kw_lat, kw_long, kw_time) and outputs their corresponding value.
        Values inside the grid are interpolated linearly and values outside of the grid are interpolated to the nearest point
        of the grid.

        "db_" inputs are things as KEV, fuel costs or similar
        "kw_" inputs denote the power plants

        INPUTS:
            db_lat: Latitude, ndarray of [float]; nx1
            db_long: Longitude, ndarray of [float]; nx1
            db_time: Time, ndarray of [datetime]; nx1
            db_values: ndarray of [float]; nx1
            kw_lat: Latitude, ndarray of [float]; jx1
            kw_long: Longitude, ndarray of [float]; jx1
            kw_time: Time, ndarray of [datetime]; jx1  

        OUTPUTS:
            kw_values: ndarray of [float]; jx1
        """

        if test_data:
            if not test_data_ordered:
                # generate random locations and values for the grid and the data points
                n_db_pts = 50
                db_lat = np.random.rand(n_db_pts) * 30 + 20
                db_long = np.random.rand(n_db_pts) * 20 - 5
                t0 = datetime.datetime.utcnow()
                db_time = t0 + np.random.randint(120, size=n_db_pts) * datetime.timedelta(days=30)
                db_values = np.random.rand(db_lat.size) * 100

                n_kw = 3
                kw_lat = np.random.rand(n_kw) * 40 + 15
                kw_long = np.random.rand(n_kw) * 30 - 10
                kw_time = t0 + np.random.randint(-20, 130, size=n_kw) * datetime.timedelta(days=30)

            else:
                # set fixed locations and values for the grid and the data points
                n_times = 5
                db_lat = np.tile(np.array([0, 0, 0, 5, 5, 5, 10, 10, 10]), n_times)
                db_long = np.tile(np.array([0, 5, 10, 0, 5, 10, 0, 5, 10]), n_times)
                t0 = datetime.datetime.utcnow()
                db_time = np.repeat(t0 + np.arange(n_times) * datetime.timedelta(days=365), 9)
                db_values = np.repeat(np.arange(10, 151, 10), 3)

                kw_lat = np.array([2.5, 7.5, 11])
                kw_long = np.array([2.5, 7.5, 5])
                kw_time = t0 + np.array([0.5, 2.5, 5]) * datetime.timedelta(days=365)

        else:
            db_lat = np.asarray(db_lat)
            db_long = np.asarray(db_long)
            db_time = np.asarray(db_time)
            db_values = np.asarray(db_values)
            kw_lat = np.asarray(kw_lat)
            kw_long = np.asarray(kw_long)
            kw_time = np.asarray(kw_time)

        # change time values from datetime to float
        db_timestamp = np.asarray([datetime.datetime.timestamp(i) for i in db_time])
        kw_timestamp = np.asarray([datetime.datetime.timestamp(i) for i in kw_time])
        # arrange inputs for griddata
        xi = np.vstack((kw_lat, kw_long, kw_timestamp))
        gridpoints = np.vstack((db_lat, db_long, db_timestamp))

        # interpolate
        interp_nearest = griddata(gridpoints.T, db_values.T, xi.T, method='nearest')
        if db_values.size <= 3:
            kw_values = interp_nearest
        else:
            interp_linear = griddata(gridpoints.T, db_values.T, xi.T, method='linear')
            # replace Nan in linear with nearest (out of range values)
            kw_values = np.where(np.isnan(interp_linear), interp_nearest, interp_linear)

        if plot_data:
            if not db_values.size <= 3:
                print('interp_linear')
                print(interp_linear)
            print('interp_nearest')
            print(interp_nearest)
            print('kw_values')
            print(kw_values)

            ax1 = plt.subplot(221, projection='3d')
            ax1.scatter(db_lat, db_long, db_timestamp, c=db_values, depthshade=False)
            ax1.scatter(kw_lat, kw_long, kw_timestamp, c='r', depthshade=False)
            ax1.set_xlabel("lat")
            ax1.set_ylabel("lon")
            ax1.set_zlabel("time")
            ax2 = plt.subplot(222)
            ax2.plot(db_long, db_timestamp, 'k.', ms=5)
            ax2.plot(kw_long, kw_timestamp, 'ro')
            plt.title('Lon/Time')
            ax2.set_ylabel("timestamp")
            ax2.set_xlabel("lon")
            ax3 = plt.subplot(223)
            ax3.plot(db_lat, db_timestamp, 'k.', ms=5)
            ax3.plot(kw_lat, kw_timestamp, 'ro')
            plt.title('Lat/Time')
            ax3.set_xlabel("lat")
            ax3.set_ylabel("timestamp")
            ax4 = plt.subplot(224)
            ax4.plot(db_lat, db_long, 'k.', ms=5)
            ax4.plot(kw_lat, kw_long, 'ro')
            plt.title('Lat/Lon')
            ax4.set_xlabel("lat")
            ax4.set_ylabel("lon")

            plt.show()

        return kw_values

    # 1D Interpolation
    def interpol_1d(self, db_time, db_values, kw_time):
        # test data or database data
        test_data = True
        plot_data = True

        """
        This function interpolates in 1 dimension
        X (time)
        Y (values)
        xi (kw_time)
        yi (kw_values, output)
        Values of xi between time.min and time.max are interpolated linearly, otherwise interpolated to nearest.

        INPUTS:
            time: ndarray of [datetime]; nx1
            values: ndarray of [float]; nx1
            kw_time: ndarray of [datetime]; mx1 (m>=1)

        OUTPUTS:
            kw_values: ndarray of [float]; mx1
        """
        if test_data:
            # create 3 time values (today, 1 and 2 years from now) and random corresponding y values
            t0 = datetime.datetime.now(timezone('utc'))
            db_time = t0 + np.arange(3) * datetime.timedelta(days=365)
            db_values = np.random.rand(3) * 100

            # create 1 or 4 test values
            kw_time = t0 + np.random.rand(4) * 30 * datetime.timedelta(days=30)
            # kw_time = t0 + np.random.rand(1) * 30 * datetime.timedelta(days=30)

        else:
            db_time = np.asarray(db_time)
            db_values = np.asarray(db_values)
            kw_time = np.asarray(kw_time)

        # change time values from datetime to float
        time = np.asarray([datetime.datetime.timestamp(i) for i in db_time])
        xi = np.asarray([datetime.datetime.timestamp(i) for i in kw_time])
        # interpolate
        interp_nearest = griddata(time.T, db_values.T, xi.T, method='nearest')
        interp_linear = griddata(time.T, db_values.T, xi.T, method='linear')
        # replace Nan in linear with nearest (out of range values)
        kw_values = np.where(np.isnan(interp_linear), interp_nearest, interp_linear)

        if plot_data:
            print('interp_linear')
            print(interp_linear)
            print('interp_nearest')
            print(interp_nearest)
            print('interp_combined')
            print(kw_values)

            ax1 = plt.axes()
            ax1.plot(time, db_values, 'k+', ms=15)
            ax1.plot(xi, kw_values, 'ro')
            ax1.set_xlabel("time")
            ax1.set_ylabel("values")
            plt.show()

        return kw_values

    # TODO remove if interpol remains normal (not async)
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

    kws = db.query(Kraftwerk).all()
    kw = db.query(Kraftwerk).first()

    stop = 1

    # define Input
    dt = 900
    t0 = datetime.datetime.now()
    t = t0 + np.arange(96) * datetime.timedelta(seconds=dt)
    inputs = {'t': t}

    h_hub = 12
    d = 26
    properties = {'h_hub': h_hub, 'd': d}

    outputs = Model.test(inputs, properties)

