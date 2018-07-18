from core import Supermodel
from core.util import Input, Output, Property
import numpy as np


# define the model class and inherit from class "Supermodel"
class Model(Supermodel):
    # model constructor
    def __init__(self, id, name: str):
        # instantiate supermodel
        super(Model, self).__init__(id, name)

        # define inputs
        self.inputs['weather'] = Input('WeatherData', unit='Global radiations[W/m^2]', info='dict')
        self.inputs['kwDaten'] = Input('PowerPlantsData', info='dict, power plant id required')

        # define outputs
        self.outputs['load'] = Output('Load', info='load of all photovoltaic power plants, value[0-1]')

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
        # Auslastung: Calculated load(Auslastung), output values are between [0-1]
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
        # PVAuslastung: Dictionary containing Power plant IDs(id) in the first list  and corresponding calculated
        # load(Auslastung) of PV power plants in second list, output values are between [0-1] except ids
        # -----------------
        #   id  Auslastung   Note: Output matrix contains the load for PV power plants only
        # -----------------
        #   2    array(96)
        #   4    array(96)
        #   6    array(96)
        ###################################################################################################################


        KWBezeichnung = 'Photovoltaik' #ForeignKeyKWTyp = 1  # ForeignKey Kraftwerkstyp z.B. 1= PV-Anlage, 2= WindKraftwerk
        KWDaten = np.array([KWDaten['id'], KWDaten['bez_kraftwerkstyp'], KWDaten['spez_info']]).transpose()

        # Extracting data corresponding solely to Photovoltaic power plant
        KraftwerksDaten = KWDaten[KWDaten[:, 1] == KWBezeichnung]

        def make_load_for_one_pv(kw_id):
            index_of_kwid_in_wetter = WetterDaten['id'].index(kw_id)
            radiation_for_kwid = WetterDaten['radiation'][index_of_kwid_in_wetter]
            radiation = np.array(radiation_for_kwid)

            auslastung = self.pvpowergenerator(radiation)
            return auslastung.tolist()

        KWid = [kw[0] for kw in KraftwerksDaten]
        loads = [make_load_for_one_pv(kw[0]) for kw in KraftwerksDaten]

        PVAuslastung = {'power_plant_id': KWid, 'load': loads}
        return PVAuslastung



