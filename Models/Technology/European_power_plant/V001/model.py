# imports from core
from core import Supermodel
from core.util import Input, Output, Property

# imports for database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from Models.Technology.European_power_plant.V001.db import Base, Kraftwerk, Kraftwerkstyp, Brennstofftyp, \
    Kraftwerksleistung, Brennstoffpreis, Entsorgungspreis, Co2Preis, create_dummy_data

# general imports
import time
import numpy as np
from scipy.interpolate import griddata
from dotenv import load_dotenv
from os import environ
import ast

# define the model class and inherit from class "Supermodel"
class Model(Supermodel):
    # model constructor
    def __init__(self, model_id, name: str):
        # instantiate supermodel
        super(Model, self).__init__(model_id, name)

        # define inputs
        self.inputs['t'] = Input('Zeit')

        # define outputs
        self.outputs['kw_park'] = Output('Kraftwerkspark')

        # define properties
        self.properties['prop1'] = Property('property1', default=10, data_type=float)

        # define persistent variables
        self.db = None

    async def func_birth(self):
        # TODO necessary in final version?
        # create database
        self.db = start_db()

    # TODO remove amend and prep if unused
    async def func_amend(self, keys=[]):
        pass

    async def func_prep(self):
        pass
        # # # calculate something
        # # prep_result = 3 * 5
        # # # pass values to peri function
        # # return prep_result

    async def func_peri(self, prep_to_peri=None):
        # # prep_result = prep_to_peri

        # get inputs
        t_in = await self.get_input('t')
        # only first time value for interpolation
        kw_time = [t_in[0]]

        print("start queries")

        """
        Naming conventions for queried and interpolated data:

        db_ : Queried directly from database or taken from another db_ value.
        kw_ : Value valid for a single power plant
        _int : interpolated values       
        """
        # query Kraftwerk
        db_kw = self.db.query(Kraftwerk).all()
        db_kw_id = [i.id for i in db_kw]
        db_kw_bez = [i.bezeichnung for i in db_kw]
        db_kw_fk_kwt = [i.fk_kraftwerkstyp for i in db_kw]
        db_kw_long = [i.long for i in db_kw]
        db_kw_lat = [i.lat for i in db_kw]

        # query Kraftwerkstyp
        db_kwt_id = [i.kraftwerkstyp.id for i in db_kw]
        db_kwt_bez = [i.kraftwerkstyp.bezeichnung for i in db_kw]
        db_kwt_bez_subtyp = [i.kraftwerkstyp.bezeichnung_subtyp for i in db_kw]
        db_kwt_fk_brennstofftyp = [i.kraftwerkstyp.fk_brennstofftyp for i in db_kw]
        db_kwt_wirkungsgrad = [i.kraftwerkstyp.wirkungsgrad for i in db_kw]
        db_kwt_opex = [i.kraftwerkstyp.spez_opex for i in db_kw]
        db_kwt_capex = [i.kraftwerkstyp.capex for i in db_kw]
        db_kwt_p_typisch = [i.kraftwerkstyp.p_typisch for i in db_kw]
        db_kwt_spez_info = [ast.literal_eval(i.kraftwerkstyp.spez_info) for i in db_kw]

        # query Brennstofftyp
        db_bst_id = [i.kraftwerkstyp.brennstofftyp.id for i in db_kw]
        db_bst_bez = [i.kraftwerkstyp.brennstofftyp.bezeichnung for i in db_kw]
        db_bst_co2emissfakt = [i.kraftwerkstyp.brennstofftyp.co2emissFakt for i in db_kw]

        # query Co2Preis
        db_co2 = self.db.query(Co2Preis).all()
        db_co2_t = [i.datetime for i in db_co2]
        db_co2_preis = [i.preis for i in db_co2]

        print("queries finished successfully")

        # Brennstoffpreis Interpolation
        bs_preis_int = []
        for kw in db_kw:
            # print("Brennstoffpreis", kw.id, kw.bezeichnung)
            if kw.kraftwerkstyp.brennstofftyp.bezeichnung == "None":
                kw_bs_preis = [float(0)]
            else:
                db_bsp = kw.kraftwerkstyp.brennstofftyp.brennstoffpreise
                db_bsp_t = [i.datetime for i in db_bsp]
                db_bsp_lat = [i.lat for i in db_bsp]
                db_bsp_long = [i.long for i in db_bsp]
                db_bsp_preis = [i.preis for i in db_bsp]

                kw_bs_preis = self.interpol_3d(db_bsp_t, db_bsp_lat, db_bsp_long, db_bsp_preis,
                                               kw.lat, kw.long, kw_time)

            bs_preis_int = bs_preis_int + kw_bs_preis

        # CO2-Preis Interpolation
        co2_preis_int = []
        for kw in db_kw:
            # print("CO2 Preis", kw.id, kw.bezeichnung)
            co2_preis_int = co2_preis_int + self.interpol_1d(db_co2_t, db_co2_preis, kw_time)

        # Entsorgungspreis Interpolation
        ents_preis_int = []
        for kw in db_kw:
            # print("Entsorgungspreis", kw.id, kw.bezeichnung)
            db_ents = kw.kraftwerkstyp.entsorgungspreise

            if len(db_ents) == 0:
                kw_ents = [float(0)]

            else:
                db_ents_t = [i.datetime for i in db_ents]
                db_ents_lat = [i.lat for i in db_ents]
                db_ents_long = [i.long for i in db_ents]
                db_ents_preis = [i.preis for i in db_ents]

                kw_ents = self.interpol_3d(db_ents_t, db_ents_lat, db_ents_long, db_ents_preis,
                                           kw.lat, kw.long, kw_time)

            ents_preis_int = ents_preis_int + kw_ents

        # P_inst Interpolation
        pinst_int = []
        for kw in db_kw:
            # print("P inst", kw.id, kw.bezeichnung)
            db_pinst = kw.kraftwerksleistungen
            db_pinst_t = [i.datetime for i in db_pinst]
            db_pinst_p = [i.power_inst for i in db_pinst]

            pinst_int = pinst_int + self.interpol_1d(db_pinst_t, db_pinst_p, kw_time)

        # Berechnung CO2-Kosten
        co2_kosten = []
        for idx, kw in enumerate(db_kw):
            # print("CO2 Kosten", kw.id, kw.bezeichnung)
            co2_emissfakt = kw.kraftwerkstyp.brennstofftyp.co2emissFakt
            wirkungsgrad = kw.kraftwerkstyp.wirkungsgrad
            co2_kosten = co2_kosten + [co2_preis_int[idx] * co2_emissfakt / wirkungsgrad]

        # Berechnung Entsorgungskosten
        ents_kosten = []
        for idx, kw in enumerate(db_kw):
            # print("Entsorgungskosten", kw.id, kw.bezeichnung)
            wirkungsgrad = kw.kraftwerkstyp.wirkungsgrad
            ents_kosten = ents_kosten + [ents_preis_int[idx] / wirkungsgrad]

        # Berechnung Brennstoffkosten
        bs_kosten = []
        for idx, kw in enumerate(db_kw):
            # print("Brennstoffkosten", kw.id, kw.bezeichnung)
            wirkungsgrad = kw.kraftwerkstyp.wirkungsgrad
            bs_kosten = bs_kosten + [bs_preis_int[idx] / wirkungsgrad]

        # TODO Alle Namen prüfen
        # TODO Namenskonvention!! (db, kwp,...)
        kwp = {"id": db_kw_id,
               "kw_bezeichnung": db_kw_bez,
               "lat": db_kw_lat,
               "long": db_kw_long,
               "p_inst": pinst_int,
               "fk_kraftwerkstyp": db_kw_fk_kwt,
               "kwt_id": db_kwt_id,
               "bez_kraftwerkstyp": db_kwt_bez,
               "bez_subtyp": db_kwt_bez_subtyp,
               "wirkungsgrad": db_kwt_wirkungsgrad,
               "opex": db_kwt_opex,
               "capex": db_kwt_capex,
               "p_typisch": db_kwt_p_typisch,
               "spez_info": db_kwt_spez_info,
               "entsorgungspreis": ents_preis_int,
               "fk_brennstofftyp": db_kwt_fk_brennstofftyp,
               "brennstofftyp_id": db_bst_id,
               "bez_brennstofftyp": db_bst_bez,
               "co2emissfakt": db_bst_co2emissfakt,
               "bs_preis": bs_preis_int,
               "co2_preis": co2_preis_int,
               "co2_kosten": co2_kosten,
               "entsorgungskosten": ents_kosten,
               "brennstoffkosten": bs_kosten,
               }

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

    # 3D Interpolation
    def interpol_3d(self, db_time, db_lat, db_long, db_values, kw_lat, kw_long, kw_time):
        """
        This function interpolates in a grid of points (db_lat,db_long,db_time) with assigned values (db_values).
        It interpolates for points given by (kw_lat, kw_long, kw_time) and outputs their corresponding value.

        Values inside the grid are interpolated linearly and values outside of the grid are interpolated to the
        nearest point of the grid.

        ATTENTION: If there are less than 4 points in db_... no grid can be formed and everything will be "interpolated"
                   to nearest.
                   Also, it is not allowed to have all points forming a plane, they must span a 3dimensional space

        |  "db_" inputs are things as KEV, fuel costs or similar
        |  "kw_" inputs denote the power plants

        INPUTS:
            |  db_lat: Latitude, list of [float]; nx1
            |  db_long: Longitude, list of [float]; nx1
            |  db_time: Time, list of [float](timestamp in s); nx1
            |  db_values: list of [float]; nx1
            |  kw_lat: Latitude, list of [float]; jx1
            |  kw_long: Longitude, list of [float]; jx1
            |  kw_time: Time, list of [float](timestamp in s); jx1

        OUTPUTS:
            kw_values: list of [float]; jx1
        """
        db_lat = np.asarray(db_lat)
        db_long = np.asarray(db_long)
        db_time = np.asarray(db_time)
        db_values = np.asarray(db_values)
        kw_lat = np.asarray(kw_lat)
        kw_long = np.asarray(kw_long)
        kw_time = np.asarray(kw_time)

        # arrange inputs for griddata
        xi = np.vstack((kw_lat, kw_long, kw_time))
        gridpoints = np.vstack((db_lat, db_long, db_time))

        # interpolate
        interp_nearest = griddata(gridpoints.T, db_values.T, xi.T, method='nearest')
        if db_values.size < 4:
            kw_values = interp_nearest
        else:
            interp_linear = griddata(gridpoints.T, db_values.T, xi.T, method='linear')
            # replace Nan in linear with nearest (out of range values)
            kw_values = np.where(np.isnan(interp_linear), interp_nearest, interp_linear)

        kw_values = kw_values.tolist()

        return kw_values

    # 2D Interpolation
    def interpol_2d(self, db_lat, db_long, db_values, kw_lat, kw_long):
        """
        This function interpolates in a grid of points (db_lat,db_long) with assigned values (db_values).
        It interpolates for points given by (kw_lat, kw_long) and outputs their corresponding value.

        Values inside the grid are interpolated linearly and values outside of the grid are interpolated
        to the nearest point of the grid.

        ATTENTION: If there are less than 3 points in db_... no grid can be formed and everything will be "interpolated"
                   to nearest.
                   Also, it is not allowed to have all points forming a line, they must span a 2dimensional space

        |  "db_" inputs are things as KEV, fuel costs or similar
        |  "kw_" inputs denote the power plants

        INPUTS:
            |  db_lat: Latitude, list of [float]; nx1
            |  db_long: Longitude, list of [float]; nx1
            |  db_values: list of [float]; nx1
            |  kw_lat: Latitude, list of [float]; jx1
            |  kw_long: Longitude, list of [float]; jx1

        OUTPUTS:
            kw_values: list of [float]; jx1
        """
        db_lat = np.asarray(db_lat)
        db_long = np.asarray(db_long)
        db_values = np.asarray(db_values)
        kw_lat = np.asarray(kw_lat)
        kw_long = np.asarray(kw_long)

        # arrange inputs for griddata
        xi = np.vstack((kw_lat, kw_long))
        gridpoints = np.vstack((db_lat, db_long))

        # interpolate
        interp_nearest = griddata(gridpoints.T, db_values.T, xi.T, method='nearest')

        if db_values.size < 3:
            kw_values = interp_nearest
        else:
            interp_linear = griddata(gridpoints.T, db_values.T, xi.T, method='linear')
            # replace Nan in linear with nearest (out of range values)
            kw_values = np.where(np.isnan(interp_linear), interp_nearest, interp_linear)

        kw_values = kw_values.tolist()

        return kw_values

    # 1D Interpolation
    def interpol_1d(self, db_time, db_values, kw_time):
        """
        This function interpolates in one dimension.
        |  X: time
        |  Y: values
        |  xi: kw_time
        |  yi: kw_values (output)

        Values inside [X(min), X(max)] are interpolated linearly,
        values outside of it are interpolated to the nearest X.
        If only one value for X and Y is provided, the output array is filled with the input value (nearest)

        INPUTS:
            |  time: list of [float](timestamp in s); nx1 (n>=2)
            |  values: list of [float]; nx1 (n>=2)
            |  kw_time: list of [float](timestamp in s); mx1 (m>=1)

        OUTPUTS:
            kw_values: list of [float]; mx1
        """

        db_time = np.asarray(db_time)
        db_values = np.asarray(db_values)
        kw_time = np.asarray(kw_time)

        if db_time.size > 1:
            # interpolate
            interp_nearest = griddata(db_time.T, db_values.T, kw_time.T, method='nearest')
            interp_linear = griddata(db_time.T, db_values.T, kw_time.T, method='linear')

            # replace Nan in linear with nearest (out of range values)
            kw_values = np.where(np.isnan(interp_linear), interp_nearest, interp_linear)

        else:
            # if only one time and one value is provided, set output to nearest (which in this case is the input value)
            kw_values = np.full(kw_time.size, db_values[0])

        kw_values = kw_values.tolist()

        return kw_values

    # TODO remove if interpol remains normal (not async)
    # define additional methods (async)
    async def extremely_complex_calculation(self, speed, time):
        distance = speed * time / self.get_property("prop1")
        return distance


def start_db():
    load_dotenv()
    db_path = environ.get("KW_DB")

    # an engine is the real DB
    engine = create_engine(db_path)

    # a session is used to communicate with the DB
    Base.metadata.bind = engine
    session = sessionmaker(bind=engine)()

    return session


def create_db():
    load_dotenv()
    db_path = environ.get("KW_DB")

    # an engine is the real DB
    engine = create_engine(db_path)

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
    # db = create_db()
    #
    # kws = db.query(Kraftwerk).all()
    # kw = db.query(Kraftwerk).first()
    #
    # stop = 1

    # define Input
    dt = 900
    t0 = time.time()
    t = [i * dt + t0 for i in range(96)]

    inputs = {'t': t}
    #
    # h_hub = 12
    # d = 26
    # properties = {'h_hub': h_hub, 'd': d}
    properties = {'prop1': 10}

    outputs = Model.test(inputs, properties)

    stop = 1
