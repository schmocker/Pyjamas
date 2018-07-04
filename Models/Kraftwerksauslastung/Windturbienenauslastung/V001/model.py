from core import Supermodel
from core.util import Input, Output, Property
import numpy as np
import math
import matplotlib as plt


# define the model class and inherit from class "Supermodel"
class Model(Supermodel):
    # model constructor
    def __init__(self, id, name: str):
        # instantiate supermodel
        super(Model, self).__init__(id, name)

        # define inputs
        self.inputs['weather'] = Input(name='WeatherData')
        self.inputs['kwDaten'] = Input(name='PowerPlantsData')

        # define outputs
        self.outputs['load'] = Output(name='Load')


    async def func_peri(self, prep_to_peri=None):
        # get inputs
        weatherdata = await self.get_input('weather')
        kwDaten = await self.get_input('kwDaten')

        #auslastung = self.calc_load(weather, kwDaten)
        auslastung = self.windturbinenauslastung(kwDaten, weatherdata)

        auslastung = auslastung




        # back converting: np.array(auslastung)


        # set output
        self.set_output("load", auslastung)



    def hubheightVSdiameter(self, Nabenhoehe):
        # Determin diameter from the given hub height
        # Use case: Internally called by windturbine()
        ###################################################################################################################
        # Input Arguments:
        # Nabenhoehe: Hub-height of wind turbine [m]
        #
        # Output Arguments:
        # Radius: Calculated radius at hub height [m]
        ###################################################################################################################
        #  Since the biggest wind turbine(Adwen AD - 180) so far made w.r.t the rotor diameter has a diameter of 180m,
        #  the parameters a and b in this equation are tuned so that it can deliver accurate results upto the rotor diameter
        #  of 478m and hub height of 250m
        #  For greater hub heights (if required) these parameters shell be tuned accordingly
        a = 3.413
        b = 0.6958
        HubHeight = Nabenhoehe
        #print("Nabenhoehe :", HubHeight)
        Diameter = 10 ** ((np.log10(HubHeight / a)) / b)
        #print("Diameter :", Diameter)
        Radius = Diameter / 2
        #print("Radius :", Radius)
        return Radius


    def windgeschwindigkeit(self, WindDaten, Nabenhoehe, BodenRauhigkeit, WindMesshoehe):
        # Calculates the wind speed a specified incoming hub-height(Nabenhoehe)
        # Use case: Internally called by windturbine()
        ###################################################################################################################
        # Input Arguments:
        # WindDaten: Measured values of wind data [m/sec]
        # Nabenhoehe: Hub-height of wind turbine [m]
        #
        # Output Arguments:
        # Cwi_h: Calculated wind speed at hub height
        ###################################################################################################################
        #
        # Windgeschwindkeiten auf verschiedene Nabenhöhen
        # Formel: Cwi,h = Cwi,ref*(ln(h/z0)/ln(href/z0))
        #
        # href: Höhe der Windmessung [m]
        # h: interessierende Höhe [m] (typischerweise Nabenhöhe der Windenergieanlage)
        # Cwi,h: Windgeschwindigkeit auf interessierender Höhe h [m/s]
        # Cwi,ref: Windgeschwindigkeit referenzhöhe(Messungshöhe) [m/s]
        # z0: Rauhigkeitslänge, Für die Rauhigkeitslänge können Werte der Tabelle 1.1-1 in WiWa_Skript_V26 verwendet werden

        href = WindMesshoehe
        Cwi_ref = WindDaten
        h = Nabenhoehe  # z.B. 100m
        z0 = BodenRauhigkeit  # z.B 0.03 für offenes landwirtschaftliches Gelände ohne Zäune und Hecken,
        # evtl. mitweitläufig verstreuten Gebäuden und sehr sanfte Hügel
        Cwi_h = Cwi_ref * ((math.log(h / z0)) / (math.log(href / z0)))
        #print("Wind at hub height :", Cwi_h)
        return Cwi_h


    def windturbine(self, WindDaten, Nabenhoehe, BodenRauhigkeit, WindMesshoehe):
        # Simulates wind power plant for specified incoming hub-hight(Nabenhoehe)
        ###################################################################################################################
        # Input Arguments:
        # WindDaten: Measured values of wind data [m/sec]
        # Nabenhoehe: Hub-height of wind turbine [m]
        #
        # Output Arguments:
        # Auslastung: Calculated Auslastung at incoming hub-height(Nabenhoehe), output values are between [0-1]
        ###################################################################################################################
        rho = 1.23  # Air density[kg / m ^ 3]
        Vnominal = 12  # Wind velocity which generates nominal output power[m/sec]
        r = self.hubheightVSdiameter(Nabenhoehe)  # Blade length or Radius[m]
        Cp = 0.40  # Efficiency[%] or Power coefficient
        A = math.pi * (r ** 2)  # Swept Area[m^2]

        # Maximum generated output power[Watt] by the wind turbine
        GeneratorNominalPower = (1 / 2) * (rho * A * (Vnominal ** 3)) * Cp
        #print("GeneratorNominalPower :", GeneratorNominalPower)

        # Produced power at different wind speeds
        # Power = (1/2)*(rho*A*(v.^3))*Cp
        #
        # v = 0:30; # Wind velocity[m/sec]  # temporary for testing purposes, will be removed
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
        #print("Auslastung eine Turbine :", Auslastung)
        return Auslastung

    def windturbinenauslastung(self, KWDaten, WetterDaten):
        # Determine the load(Auslastung) wind turbine
        ###################################################################################################################
        # Input Arguments:
        # KWDaten: Matrix holding different parameters of power plants
        # ------------------------------------------------------------------
        # KWIDs FKKWT    Power[W]    Nabenhöhe        Z0        Capex   Opex
        # ------------------------------------------------------------------
        #   1    2(WT)   1000000       150           0.03         1     0.01
        #   2    1(pv)   2000000        0          nothing =0     2     0.02
        #   3    2(WT)   3000000       200           0.03         3     0.03
        #   4    1(pv)   4000000        0          nothing =0     4     0.04
        #   5    2(WT)   5000000       250           0.03         5     0.05
        #   6    1(pv)   6000000        0          nothing =0     6     0.06
        #   8    3()     1000000        0          nothing =0     7     0.07
        #   10   3()     1000000        0          nothing =0     8     0.08
        #   11   4()     1000000        0          nothing =0     9     0.09
        # [KW-ID, FK-KWT, Power, Nabenhöhe, Weitere Parameter(Z0), Capex, Opex, KEV, Brennstoffkosten, Entsorgungskostne, CO2-Kosten]
        #
        # WetterDaten: Matrix holding Power plant IDs(KWIDs) and weather data for all types of power plants as shown in
        # the following table
        # -------------------
        # KWIDs   WetterDaten
        # -------------------
        #   1     array(96)
        #   2     array(96)
        #   3     array(96)
        #   4     array(96)
        #   5     array(96)
        #   6     array(96)
        #   8     array(96)
        #   10    array(96)
        #   11    array(96)
        #
        # Output Arguments:
        # WTAuslastung: Matrix containing KWIDs in the first column  and corresponding calculated
        # load(Auslastung) of wind turbine in following 96 columns, output values are between [0-1] except KWIDs
        # -----------------
        # KWIDs  Auslastung   Note: Output matrix contains only load for wind turbines
        # -----------------
        #   2    array(96)
        #   4    array(96)
        #   6    array(96)
        ###################################################################################################################
        ForeignKeyKWTyp = 2  # ForeignKey Kraftwerkstyp z.B. 1= PV-Anlage, 2= WindKraftwerk


        KWDaten = np.array([ KWDaten['id'], KWDaten['fk_kwt'], KWDaten['spez_info']]).transpose()
        # Wetter = np.array([ WetterDaten['id'], WetterDaten['wetter']]).transpose()



        # Extracting data corresponding solely to wind turbines, by selecting rows of KWDaten where Foreign-Key= 2
        KraftwerksDaten = KWDaten[KWDaten[:, 1] == ForeignKeyKWTyp]

        def make_load_for_one_wt(kw_id, NH, Z0):

            index_of_kwid_in_wetter = WetterDaten['id'].index(kw_id)
            wind_for_kwid = WetterDaten['windspeed'][index_of_kwid_in_wetter]
            wind_messhoehe = WetterDaten['windmesshoehe'][index_of_kwid_in_wetter]
            wind = np.array(wind_for_kwid)

            auslastung = self.windturbine(wind, NH, Z0, wind_messhoehe)
            plt.plot(auslastung)
            plt.show()
            return auslastung.tolist()

        id = [kw[0] for kw in KraftwerksDaten]
        load = [make_load_for_one_wt(kw[0], kw[2]['NH'], kw[2]['Z0']) for kw in KraftwerksDaten]

        WTAuslastung = {'id': id, 'load': load}


        #NH = [kw[3]['NH'] for kw in KraftwerksDaten]
        #Z0 = [kw[3]['Z0'] for kw in KraftwerksDaten]

        #NH = np.array([NH]).transpose()
        #KraftwerksDaten = np.append(KraftwerksDaten, NH, axis=1)

        #Z0 = np.array([Z0]).transpose()
        #KraftwerksDaten = np.append(KraftwerksDaten, Z0, axis=1)

        # Selecting KWIDs of filtered wind turbines
        ####KWID_WT = KraftwerksDaten[:, 0]
        ####print("KWID_WT: ", KWID_WT)
        # Extracting weather data corresponding solely to wind turbines, by selecting rows of incoming WetterDaten where
        # KWID of WetterDaten = KWID_PV
        ####BoolWeather = np.in1d(WetterDaten[:, 0],
        #                  KWID_WT)  # 1D vector holding TRUE/FALSE, TRUE values corresponds to PV data
        ######WTWetterDaten = WetterDaten[BoolWeather == True]

        #########WTAuslastung = np.zeros(WTWetterDaten.shape)



        '''
        for i in range(0, WTWetterDaten.shape[0]):
            WindDaten = WTWetterDaten[i, 1:]
            BodenRauhigkeit = KraftwerksDaten[i, 3]['Z0']
            #print("BodenRauhigkeit: ", BodenRauhigkeit)
            Nabenhoehe = KraftwerksDaten[i, 3]['NH']
            Auslastung = self.windturbine(WindDaten, Nabenhoehe, BodenRauhigkeit)
            # PVAuslastung[KWID(i), Auslastung(0:96)]
            WTAuslastung[i] = np.hstack((KraftwerksDaten[i, 0], Auslastung))
            #plt.plot(Auslastung)
            #plt.show()
        '''

        #print("Load all PPs: ", WTAuslastung)
        return WTAuslastung





