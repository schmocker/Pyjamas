# imports from core
from pyjamas_core import Supermodel
from pyjamas_core.util import Input, Output

# imports for database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from Models.Technology.European_power_plant.V001.db.db_declarative import Base, Kraftwerk, Co2Preis
# all other tables are used indirectly starting at Kraftwerk

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

        # define persistent variables
        self.db = None
        self.kwp = None

    async def func_birth(self):
        # start database connection
        self.db = start_db()

    async def func_peri(self, prep_to_peri=None):
        if self.kwp is None:

            # get inputs
            t_in = await self.get_input('t')
            # use only first time value for interpolation (as list)
            kw_time = [t_in[0]]

            time0 = time.time()
            print(f"start database queries")

            """
            Naming conventions for queried and interpolated data:
                db_ : Queried directly from database or taken from another db_ value.
                kw_ : Value valid for a single power plant
                _int : interpolated values       
            """
            # ---------------------- QUERYS -----------------------------------------------
            # query Kraftwerk
            db_kw = self.db.query(Kraftwerk).order_by(Kraftwerk.id).all()
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
            db_kwt_p_typisch = [i.kraftwerkstyp.p_typisch for i in db_kw]
            db_kwt_spez_info = [ast.literal_eval(i.kraftwerkstyp.spez_info) for i in db_kw]  # change string to dict

            # query Brennstofftyp
            db_bst_id = [i.kraftwerkstyp.brennstofftyp.id for i in db_kw]
            db_bst_bez = [i.kraftwerkstyp.brennstofftyp.bezeichnung for i in db_kw]
            db_bst_co2emissfakt = [i.kraftwerkstyp.brennstofftyp.co2emissFakt for i in db_kw]

            # query Co2Preis
            db_co2 = self.db.query(Co2Preis).all()
            db_co2_t = [i.datetime for i in db_co2]
            db_co2_preis = [i.preis for i in db_co2]

            time1 = time.time()
            d_time = time1 - time0
            print(f"-> database queries finished successfully in {d_time}s")
            print("start interpolation")

            # ---------------------- INTERPOLATION ----------------------------------------
            # Brennstoffpreis Interpolation
            bs_preis_int = []
            for kw in db_kw:
                if kw.kraftwerkstyp.brennstofftyp.bezeichnung == "None":
                    kw_bs_preis = [float(0)]  # Brennstoffpreis to zero if type equals "None"
                else:
                    db_bsp = kw.kraftwerkstyp.brennstofftyp.brennstoffpreise
                    db_bsp_t = [i.datetime for i in db_bsp]
                    db_bsp_lat = [i.lat for i in db_bsp]
                    db_bsp_long = [i.long for i in db_bsp]
                    db_bsp_preis = [i.preis for i in db_bsp]

                    kw_bs_preis = self.interpol_3d(db_bsp_t, db_bsp_lat, db_bsp_long, db_bsp_preis,
                                                   kw.lat, kw.long, kw_time)

                # append new kw_bs_preis (list) to existing list
                bs_preis_int = bs_preis_int + kw_bs_preis

            # CO2-Preis Interpolation
            co2_preis_int = [self.interpol_1d(db_co2_t, db_co2_preis, kw_time)[0] for _ in db_kw]

            # Entsorgungspreis Interpolation
            ents_preis_int = []
            for kw in db_kw:
                db_ents = kw.kraftwerkstyp.entsorgungspreise

                # check if values are present (some powerplant types don't have a value, e.g. wind, solar,...)
                if len(db_ents) == 0:
                    kw_ents = [float(0)]  # set to zero if no values present
                else:
                    db_ents_t = [i.datetime for i in db_ents]
                    db_ents_lat = [i.lat for i in db_ents]
                    db_ents_long = [i.long for i in db_ents]
                    db_ents_preis = [i.preis for i in db_ents]

                    kw_ents = self.interpol_3d(db_ents_t, db_ents_lat, db_ents_long, db_ents_preis,
                                               kw.lat, kw.long, kw_time)

                # append new ents_preis_kw (list) to existing list
                ents_preis_int = ents_preis_int + kw_ents

            # Installed power Interpolation
            pinst_int = []
            for kw in db_kw:
                db_pinst = kw.kraftwerksleistungen
                db_pinst_t = [i.datetime for i in db_pinst]
                db_pinst_p = [i.power_inst for i in db_pinst]

                # append new pinst (list) to existing list
                pinst_int = pinst_int + self.interpol_1d(db_pinst_t, db_pinst_p, kw_time)

            # Variable Opex Interpolation
            varopex_int = []
            for kw in db_kw:
                db_varopex = kw.kraftwerkstyp.var_opex
                db_varopex_t = [i.datetime for i in db_varopex]
                db_varopex_preis = [i.preis for i in db_varopex]

                # append new opex (list) to existing list
                varopex_int = varopex_int + self.interpol_1d(db_varopex_t, db_varopex_preis, kw_time)

            # Capex Interpolation
            capex_int = []
            for kw in db_kw:
                db_capex = kw.kraftwerkstyp.capex
                db_capex_t = [i.datetime for i in db_capex]
                db_capex_preis = [i.preis for i in db_capex]

                # append new opex (list) to existing list
                capex_int = capex_int + self.interpol_1d(db_capex_t, db_capex_preis, kw_time)

            time2 = time.time()
            d_time = time2 - time1
            print(f"-> interpolation finished successfully in {d_time}s")
            print("start calculation")

            # ---------------------- CALCULATION ------------------------------------------
            # calculation CO2-Kosten
            co2_kosten = [a*b/c for a, b, c in zip(co2_preis_int, db_bst_co2emissfakt, db_kwt_wirkungsgrad)]

            # calculation Entsorgungskosten
            ents_kosten = [a/b for a, b in zip(ents_preis_int, db_kwt_wirkungsgrad)]

            # calculation Brennstoffkosten
            bs_kosten = [a/b for a, b in zip(bs_preis_int, db_kwt_wirkungsgrad)]

            # calculation Grenzkosten (Marginal Cost)
            grenz_kosten = [a+b+c+d for a, b, c, d in zip(varopex_int, bs_kosten, co2_kosten, ents_kosten)]

            time3 = time.time()
            d_time = time3 - time2
            print(f"-> calculation finished successfully in {d_time}s")
            print("start defining output")

            # ---------------------- DEFINE OUTPUTS ---------------------------------------
            # output sorted by id, units in comments
            kwp = {"id": db_kw_id,  # [-]
                   "kw_bezeichnung": db_kw_bez,  # [-]
                   "lat": db_kw_lat,  # [deg]
                   "long": db_kw_long,  # [deg]
                   "p_inst": pinst_int,  # [W]
                   "fk_kraftwerkstyp": db_kw_fk_kwt,  # [-]
                   "kwt_id": db_kwt_id,  # [-]
                   "bez_kraftwerkstyp": db_kwt_bez,  # [-]
                   "bez_subtyp": db_kwt_bez_subtyp,  # [-]
                   "wirkungsgrad": db_kwt_wirkungsgrad,  # [-]
                   "var_opex": varopex_int,  # [€/J]
                   "capex": capex_int,  # [€/W_el]
                   "p_typisch": db_kwt_p_typisch,  # [W]
                   "spez_info": db_kwt_spez_info,  # dict with "NH" [m] and "Z0" [m]
                   "entsorgungspreis": ents_preis_int,  # [€/J_bs]
                   "fk_brennstofftyp": db_kwt_fk_brennstofftyp,  # [-]
                   "brennstofftyp_id": db_bst_id,  # [-]
                   "bez_brennstofftyp": db_bst_bez,  # [-]
                   "co2emissfakt": db_bst_co2emissfakt,  # [kg_CO2/J_bs]
                   "bs_preis": bs_preis_int,  # [€/J_bs]
                   "co2_preis": co2_preis_int,  # [€/kg_CO2]
                   "co2_kosten": co2_kosten,  # [€/J_el]
                   "entsorgungskosten": ents_kosten,  # [€/J_el]
                   "brennstoffkosten": bs_kosten,  # [€/J_el]
                   "grenzkosten": grenz_kosten,  # [€/J_el]
                   }

            time4 = time.time()
            d_time = time4 - time3
            print(f"-> defining output finished successfully in {d_time}s")
            d_time = time4 - time0
            print(f"-> -> -> eu power plant finished successfully in {d_time}s")
            print("")

            self.kwp = kwp

        self.set_output("kw_park", self.kwp)

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

        |  "db_" inputs are things as prices or similar
        |  "kw_" inputs denote the power plants

        INPUTS:
            |  db_lat: Latitude, list of [float]; nx1
            |  db_long: Longitude, list of [float]; nx1
            |  db_time: Time, list of [float](timestamp in [s]); nx1
            |  db_values: list of [float]; nx1
            |  kw_lat: Latitude, list of [float]; jx1
            |  kw_long: Longitude, list of [float]; jx1
            |  kw_time: Time, list of [float](timestamp in [s]); jx1

        OUTPUTS:
            kw_values: list of [float]; jx1
        """
        # change to ndarray for usage in griddata
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

        # if not enough db-points present only interpolate nearest (see docstring)
        if db_values.size < 4:
            kw_values = interp_nearest
        else:
            interp_linear = griddata(gridpoints.T, db_values.T, xi.T, method='linear')
            # replace Nan (out of range values) in linear with nearest
            kw_values = np.where(np.isnan(interp_linear), interp_nearest, interp_linear)

        # make output list
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

        |  "db_" inputs are things as prices or similar
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
        # change to ndarray for usage in griddata
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

        # if not enough db-points present only interpolate nearest (see docstring)
        if db_values.size < 3:
            kw_values = interp_nearest
        else:
            interp_linear = griddata(gridpoints.T, db_values.T, xi.T, method='linear')
            # replace Nan (out of range values) in linear with nearest
            kw_values = np.where(np.isnan(interp_linear), interp_nearest, interp_linear)

        # make output list
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
            |  time: list of [float](timestamp in [s]); nx1
            |  values: list of [float]; nx1
            |  kw_time: list of [float](timestamp in [s]); mx1

        OUTPUTS:
            kw_values: list of [float]; mx1
        """
        # change to ndarray for usage in griddata
        db_time = np.asarray(db_time)
        db_values = np.asarray(db_values)
        kw_time = np.asarray(kw_time)

        if db_time.size > 1:
            # interpolate
            interp_nearest = griddata(db_time.T, db_values.T, kw_time.T, method='nearest')
            interp_linear = griddata(db_time.T, db_values.T, kw_time.T, method='linear')
            # replace Nan (out of range values) in linear with nearest
            kw_values = np.where(np.isnan(interp_linear), interp_nearest, interp_linear)
        else:
            # if only one time and one value is provided, set output to nearest (which in this case is the input value)
            kw_values = np.full(kw_time.size, db_values[0])

        # make output list
        kw_values = kw_values.tolist()
        return kw_values


# Start database connection from path provided in .env
def start_db():
    load_dotenv()
    db_path = environ.get("KW_DB")

    # an engine is the real DB
    engine = create_engine(db_path)

    # a session is used to communicate with the DB
    Base.metadata.bind = engine
    session = sessionmaker(bind=engine)()

    return session


if __name__ == "__main__":
    # define Input, build time array
    dt = 900
    t0 = time.time()
    t = [i * dt + t0 for i in range(96)]

    inputs = {'t': t}
    properties = {}

    # test model
    test = Model.test(inputs, properties)

    stop = 1
