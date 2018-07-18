from core import Supermodel
from core.util import Input, Output, Property
import numpy as np
import math


# define the model class and inherit from class "Supermodel"
class Model(Supermodel):
    # model constructor
    def __init__(self, id, name: str):
        # instantiate supermodel
        super(Model, self).__init__(id, name)

        # define inputs
        self.inputs['weather'] = Input('WeatherData', unit='Wind speed[m/s], Wind measurement height[m]', info='dict')
        self.inputs['kwDaten'] = Input('PowerPlantsData',unit='Hub-height[m], Ground roughness length[m]', info='dict')

        # define outputs
        self.outputs['load'] = Output('Load', info='load of all wind turbines, value[0-1]')

    '''   
        # define properties
        # Property(<initial value>,<type>,<info dictionary>)
        self.properties['Nabenhoehe'] = Property(10, float, name='hub height', unit='m')
        self.properties['Bodenrauigkeit'] = Property(10, float, name='Surface Roughness', unit='m')

        self.nabenhoehe = None
        self.bodenrauhigkeit = None

    async  def func_birth(self):
        await self.func_amend(['Nabenhoehe', 'Bodenrauigkeit'])

    async def func_amend(self, keys=[]):
        if 'Nabenhoehe' in keys:
            self.nabenhoehe = self.get_property('Nabenhoehe')

        if 'Bodenrauigkeit' in keys:
            self.nabenhoehe = self.get_property('Bodenrauigkeit')
    '''


    async def func_peri(self, prep_to_peri=None):
        # get inputs
        weatherdata = await self.get_input('weather')
        kwDaten = await self.get_input('kwDaten')

        #auslastung = self.calc_load(weather, kwDaten)
        auslastung = self.windturbinenauslastung(kwDaten, weatherdata)

        auslastung = auslastung
        # set output
        self.set_output("load", auslastung)



    def hubheightVSdiameter(self, Nabenhoehe):
        # Determin diameter from the given hub height
        # Use case: Internally called by windturbine()
        ################################################################################################################
        # Input Arguments:
        # Nabenhoehe: Hub-height of wind turbine [m]
        #
        # Output Arguments:
        # Radius: Calculated radius at hub height [m]
        ################################################################################################################
        #  Since the biggest wind turbine(Adwen AD - 180) so far made w.r.t the rotor diameter has a diameter of 180m,
        #  the parameters a and b in this equation are tuned so that it can deliver accurate results upto the rotor diameter
        #  of 478m and hub height of 250m
        #  For greater hub heights (if required) these parameters shell be tuned accordingly
        a = 3.413
        b = 0.6958
        HubHeight = Nabenhoehe
        Diameter = 10 ** ((np.log10(HubHeight / a)) / b)
        Radius = Diameter / 2
        return Radius


    def windgeschwindigkeit(self, WindDaten, Nabenhoehe, BodenRauhigkeit, WindMesshoehe):
        # Calculates the wind speed at specified incoming hub-height(Nabenhoehe)
        # Use case: Internally called by windturbine()
        ################################################################################################################
        # Input Arguments:
        # WindDaten: Measured values of wind data [m/s]
        # Nabenhoehe: Hub-height of wind turbine [m]
        # BodenRauhigkeit: Bodenrauigkeitslänge [m]
        # WindMesshoehe: Höhe der Windmessung [m]
        #
        # Output Arguments:
        # Cwi_h: Calculated wind speed at hub height [m/s]
        ################################################################################################################
        #
        # Windgeschwindkeiten auf verschiedene Nabenhöhen
        # Formel: Cwi,h = Cwi,ref*(ln(h/z0)/ln(href/z0))
        #
        # href: Höhe der Windmessung [m]
        # h: interessierende Höhe [m] (typischerweise Nabenhöhe der Windenergieanlage)
        # Cwi,h: Windgeschwindigkeit auf interessierender Höhe h [m/s]
        # Cwi,ref: Windgeschwindigkeit referenzhöhe(Messungshöhe) [m/s]
        # z0: Rauigkeitslänge, Für die Werte der Rauhigkeitslänge siehe der Tabelle 1.1-1 in WiWa_Skript_V26

        href = WindMesshoehe
        Cwi_ref = WindDaten
        h = Nabenhoehe  # z.B. 100m
        z0 = BodenRauhigkeit    # z.B 0.03 für offenes landwirtschaftliches Gelände ohne Zäune und Hecken,
                                # evtl. mitweitläufig verstreuten Gebäuden und sehr sanfte Hügel
        Cwi_h = Cwi_ref * ((math.log(h / z0)) / (math.log(href / z0)))
        return Cwi_h


    def windturbine(self, WindDaten, Nabenhoehe, BodenRauhigkeit, WindMesshoehe):
        # Simulates wind power plant for specified incoming hub-hight(Nabenhoehe)
        ################################################################################################################
        # Input Arguments:
        # WindDaten: Measured values of wind data [m/sec]
        # Nabenhoehe: Hub-height of wind turbine [m]
        # BodenRauhigkeit: Bodenrauigkeitslänge [m]
        # WindMesshoehe: Höhe der Windmessung [m]
        #
        # Output Arguments:
        # Auslastung: Calculated Auslastung at incoming hub-height, output values are between [0-1]
        ################################################################################################################
        rho = 1.23  # Air density[kg / m ^ 3]
        Vnominal = 12  # Wind velocity which generates nominal output power[m/sec]
        r = self.hubheightVSdiameter(Nabenhoehe)  # Blade length or Radius[m]
        Cp = 0.40  # Efficiency[%] or Power coefficient
        A = math.pi * (r ** 2)  # Swept Area[m^2]

        # Maximum generated output power[Watt] by the wind turbine
        GeneratorNominalPower = (1 / 2) * (rho * A * (Vnominal ** 3)) * Cp

        # Produced power at different wind speeds
        # Power = (1/2)*(rho*A*(v.^3))*Cp
        v = self.windgeschwindigkeit(WindDaten, Nabenhoehe, BodenRauhigkeit, WindMesshoehe)  # Wind velocity[m/sec] at specific (e.g. 100m) hub height
        TheoraticalPower = (1 / 2) * (rho * A * (v ** 3)) * Cp

        # Output Power produced by the wind turbine[watt]
        PowerOutput = TheoraticalPower
        for i in range(0, WindDaten.shape[0]):
            if (v[i] < 4 or v[i] >= 25):  # Phase-1 and Phase-4 of wind turbine's power generation curve
                PowerOutput[i] = 0

            if (PowerOutput[i] >= GeneratorNominalPower):  # Phase-3 of wind turbine's power generation curve
                PowerOutput[i] = GeneratorNominalPower

        PowerOutput = PowerOutput / 1e6  # Watt to MW conversion
        GeneratorNominalPower = GeneratorNominalPower / 1e6  # Watt to MW conversion

        Auslastung = PowerOutput / GeneratorNominalPower  # Auslastung = ProducedPower/Pnominal
        return Auslastung

    def windturbinenauslastung(self, KWDaten, WetterDaten):
        # Determine the load(Auslastung) of wind turbine
        ###################################################################################################################
        # Input Arguments:
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
        # WetterDaten: Dictionary holding Power plant IDs(id) and weather data for all types of power plants
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
        #
        # Output Arguments:
        # WTAuslastung: Dictionary containing Power plant IDs(id) in the first list and corresponding calculated
        # load(Auslastung) of wind turbine in second list, output values are between [0-1] except ids
        # -----------------
        #   id   Auslastung   Note: Output matrix contains the load of wind turbines only
        # -----------------
        #   2    array(96)
        #   4    array(96)
        #   6    array(96)
        ###################################################################################################################

        KWBezeichnung = 'Windturbine' #ForeignKeyKWTyp = 2  # ForeignKey Kraftwerkstyp z.B. 1= PV-Anlage, 2= WindKraftwerk

        KWDaten = np.array([ KWDaten['id'], KWDaten['bez_kraftwerkstyp'], KWDaten['spez_info']]).transpose()

        # Extracting data corresponding solely to wind turbines
        KraftwerksDaten = KWDaten[KWDaten[:, 1] == KWBezeichnung]

        def make_load_for_one_wt(kw_id, NH, Z0):
            kw_id = int(kw_id)
            index_of_kwid_in_wetter = WetterDaten['id'].index(kw_id)
            wind_for_kwid = WetterDaten['windspeed'][index_of_kwid_in_wetter]
            wind_messhoehe = WetterDaten['windmesshoehe'][index_of_kwid_in_wetter]
            wind = np.array(wind_for_kwid)

            auslastung = self.windturbine(wind, NH, Z0, wind_messhoehe)
            return auslastung.tolist()

        KWid = [kw[0] for kw in KraftwerksDaten]
        loads = [make_load_for_one_wt(kw[0], kw[2]['NH'], kw[2]['Z0']) for kw in KraftwerksDaten]

        WTAuslastung = {'power_plant_id': KWid, 'load': loads}
        return WTAuslastung





