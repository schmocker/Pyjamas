from core import Supermodel
from core.util import Input, Output, Property
import numpy as np
import matplotlib.pyplot as plt

# define the model class and inherit from class "Supermodel"
class Model(Supermodel):
    # model constructor
    def __init__(self, id, name: str):
        # instantiate supermodel
        super(Model, self).__init__(id, name)

        # define inputs
        self.inputs['weather'] = Input(name='WeatherData', unit='dict')
        self.inputs['kwDaten'] = Input(name='PowerPlantsData', unit='dict')

        # define outputs
        self.outputs['load'] = Output(name='Load', unit='value[0-1]')

    async def func_peri(self, prep_to_peri=None):
        # get inputs
        weather = await self.get_input('weather')
        kwDaten = await self.get_input('kwDaten')

        load = self.pvauslastung(kwDaten, weather)

        # set output
        self.set_output("load", load)



    # define additional methods (normal)
    def pvpowergenerator(self, GlobalRadiations):
        # Simulates photovoltaic power plant for specified incoming solar irradiance
        ###################################################################################################################
        # Input Arguments:
        # GlobalRadiations: Measured values of global irradiance on horizontal surface [W/m^2]
        #
        # Output Arguments:
        # Auslastung: Calculated Auslastung, output values are between [0-1]
        ###################################################################################################################
        # 75% of total global radiation are captured by the tilted surface oriented towards specified direction (e.g south)
        GlobalRadiationLoss = 0.25
        RadiationOnTiltedSurface = (1 - GlobalRadiationLoss) * GlobalRadiations

        Tmodule = 25  # Standard Test Condition temperature
        Pnominal = 1000  # 1kW base power

        # Output reduction[W] = (Actuell module temperature[°C] - 25°C) * (-0.0034 /°C) * Module's nominal power[W])
        OutputReduction = (Tmodule - 25) * 0.0034 * Pnominal
        # PVs Output[W] = (Module's nominal power[W] - Output reduction[W])*(Solar irradiations [W/m2] /1000 W/m2)
        DcPout = (Pnominal - OutputReduction) * (RadiationOnTiltedSurface / 1000)

        Auslastung = DcPout / Pnominal  # Auslastung = ProducedPower/Pnominal
        return Auslastung


    def pvauslastung(self, KWDaten, WetterDaten):
        # Determine the load(Auslastung) PV power plant
        ###################################################################################################################
        # Input Arguments:
        # KWDaten: Matrix holding Power plant IDs(KWIDs), foreign keys (FKs-KWT), Scaling Power, Weather data of
        #          all power plants and other parameters as shown in the following table
        # ----------------------------------------------------
        # KWIDs FKKWT    Power[W]    Nabenhöhe        Z0
        # ----------------------------------------------------
        #   1    2(WT)   1000000       150           0.03
        #   2    1(pv)   2000000        0          nothing =0
        #   3    2(WT)   3000000       200           0.03
        #   4    1(pv)   4000000        0          nothing =0
        #   5    2(WT)   5000000       250           0.03
        #   6    1(pv)   6000000        0          nothing =0
        #   8    3()     1000000        0          nothing =0
        #   10   3()     1000000        0          nothing =0
        #   11   4()     1000000        0          nothing =0
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
        # PVAuslastung: Matrix containing KWIDs in the first column  and corresponding calculated
        # load(Auslastung) of PV power plant in following 96 columns, output values are between [0-1] except KWIDs
        # -----------------
        # KWIDs  Auslastung   Note: Output matrix contains only load for PV power plants
        # -----------------
        #   2    array(96)
        #   4    array(96)
        #   6    array(96)
        ###################################################################################################################
        ###################################################################################################################
        KWBezeichnung = 'PV' #ForeignKeyKWTyp = 1  # ForeignKey Kraftwerkstyp z.B. 1= PV-Anlage, 2= WindKraftwerk
        KWDaten = np.array([KWDaten['id'], KWDaten['kw_bezeichnung'], KWDaten['spez_info']]).transpose()

        # Extracting data corresponding solely to wind turbines, by selecting rows of KWDaten where Foreign-Key= 2
        KraftwerksDaten = KWDaten[KWDaten[:, 1] == KWBezeichnung]

        def make_load_for_one_pv(kw_id):
            index_of_kwid_in_wetter = WetterDaten['id'].index(kw_id)
            radiation_for_kwid = WetterDaten['radiation'][index_of_kwid_in_wetter]
            radiation = np.array(radiation_for_kwid)

            auslastung = self.pvpowergenerator(radiation)
            return auslastung.tolist()

        KWid = [kw[0] for kw in KraftwerksDaten]
        load = [make_load_for_one_pv(kw[0]) for kw in KraftwerksDaten]

        PVAuslastung = {'id': KWid, 'load': load}
        return PVAuslastung



