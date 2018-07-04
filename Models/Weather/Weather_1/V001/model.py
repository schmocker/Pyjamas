from core import Supermodel
from core.util import Input, Output, Property


# define the model class and inherit from class "Supermodel"
class Model(Supermodel):
    # model constructor
    def __init__(self, id, name: str):
        # instantiate supermodel
        super(Model, self).__init__(id, name)

        # define inputs
        self.inputs['mode'] = Input(name='modus', unit='-', info="modus (live or simulation")
        self.inputs['KW'] = Input(name='KW info', unit='-', info="KW information (id, lat, lon)")
        self.inputs['date'] = Input(name='Time vector', unit='s', info="Time in utc")

        # define outputs
        self.outputs['weather_data'] = Output(name='weather data of KWs')

        # define properties
        self.properties['T_offset'] = Property(0, float, name='temperature offset', unit='%', info="offset of temperature in %")
        self.properties['u_offset'] = Property(0, float, name='wind speed offset', unit='%', info="offset of wind speed in %")
        self.properties['P_offset'] = Property(0, float, name='radiation offset', unit='%', info="offset of radiation in %")
        self.properties['ref_year'] = Property(0, float, name='reference year', unit='%', info="reference year for modeled weather")

        # define persistent variables
        self.model_pars = None

    # async def func_birth(self):
    #     pass


    # async def func_prep(self):
    #     # calculate something
    #     prep_result = 3 * 5
    #     # pass values to peri function
    #     return prep_result
    # ???????????? KW Daten vorbereiten / extrahieren?


    async def func_peri(self, prep_to_peri=None):

        print("a")
        # get inputs
        mode = await self.get_input('mode')
        KW_data = await self.get_input('KW')
        dates = await self.get_input('date')

        # loop over KW's
        # - initialization
        out_ids = []
        out_T = []
        out_u = []
        out_P = []
        len_id = KW_data["ID"].__len__()

        # - loop
        for it in range(0,len_id):

            id_it = KW_data["ID"][it]
            long = KW_data["Longitude"][it]
            lat = KW_data["Latitude"][it]

            # selection of weather model based on mode
            if mode == 'live':
                w_data = 1
                w_data_it = [self.weather_API(long, lat, tt) for tt in dates]

            else:
                w_data = 2
                w_data_it = [self.weather_historic(long, lat, tt, self.get_property('ref_year')) for tt in dates]


            # append data
            out_ids.append(id_it)
            out_T.append(w_data_it[0][0])
            out_u.append(w_data_it[0][1])
            out_P.append(w_data_it[0][2])

        # create dict
        weather_data = dict(zip(["ID", "Temperature", "Wind_speed", "Radiation"], [out_ids, out_T, out_u, out_P]))

        # set output
        self.set_output("weather_data", weather_data)


    def weather_API(self, long, lat, date):

        T_it = 20
        u_it = 10
        P_it = 1000

        # offset
        T_it = T_it*(1+self.get_property("T_offset")/100)
        u_it = u_it * (1 + self.get_property("u_offset") / 100)
        P_it = P_it * (1 + self.get_property("P_offset") / 100)

        w_data_it = [T_it, u_it, P_it]

        return w_data_it

    def weather_historic(self, long, lat, date, year):

        T_it = 21
        u_it = 11
        P_it = 1001

        # offset
        T_it = T_it*(1+self.get_property("T_offset")/100)
        u_it = u_it * (1 + self.get_property("u_offset") / 100)
        P_it = P_it * (1 + self.get_property("P_offset") / 100)

        w_data_it = [T_it, u_it, P_it]

        return w_data_it
