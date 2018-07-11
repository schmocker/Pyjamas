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
        self.inputs['WTAuslastung'] = Input('LoadWindTurbine', info='value[0-1]')
        self.inputs['PVAuslastung'] = Input('LoadPhotovoltaic', info='value[0-1]')
        self.inputs['LaufwasserKWAuslastung'] = Input('LoadRunningWaterPowerPlant', info='value[0-1]')
        self.inputs['SpeicherwasserKWAuslastung'] = Input('LoadStoragePowerPlant', info='value[0-1]')
        self.inputs['KWDaten'] = Input('PowerPlantsData', info='IDs extracted from PowerPlantData')

        # define outputs
        self.outputs['GemeinsameAuslastung'] = Output('CombinedLoad', info='value[0-1]')

    async def func_peri(self, prep_to_peri=None):
        # get inputs
        WTAuslastung = await self.get_input('WTAuslastung')
        PVAuslastung = await self.get_input('PVAuslastung')
        LWKWAuslastung = await self.get_input('LaufwasserKWAuslastung')
        SWKWAuslastung = await self.get_input('SpeicherwasserKWAuslastung')
        KWDaten = await self.get_input('KWDaten')

        # calculate
        GemeinsameAuslastung = self.auslastungallerKWs(WTAuslastung, PVAuslastung, LWKWAuslastung, SWKWAuslastung, KWDaten)

        # set output
        self.set_output("GemeinsameAuslastung", GemeinsameAuslastung)


    # define additional methods (normal)
    def auslastungallerKWs(self, WTauslastung, PVauslastung, LWKWauslastung, SWKWAuslastung, KWDaten):
        # Determine the load(Auslastung) of each power plant according to incoming Power plant key /Foreign Keys
        # separately and then combine them together in a matrix to form combined loading
        ###################################################################################################################
        # Input Arguments:
        ## WTAuslastung: Dictionary containing KWIDs in the first column  and corresponding calculated
        # load(Auslastung) of wind turbine in following 96 columns, output values are between [0-1] except KWIDs
        # -----------------
        # KWIDs  Auslastung   Note: Output matrix contains only load for wind turbines
        # -----------------
        #   2    array(96)
        #   4    array(96)
        #   6    array(96)
        #
        # PVAuslastung: Dictionary containing KWIDs in the first column  and corresponding calculated
        # load(Auslastung) of PV power plant in following 96 columns, output values are between [0-1] except KWIDs
        # -----------------
        # KWIDs  Auslastung   Note: Output matrix contains only load for PV power plants
        # -----------------
        #   2    array(96)
        #   4    array(96)
        #   6    array(96)
        #
        # KWDaten: Dictionary holding the different parameters of power plants
        # ------------------------------------------------------------------------------------
        #   id  fk_kwt   kw_bezeichnung    power[W]         spez_info             Capex   Opex
        # ------------------------------------------------------------------------------------
        #   1     2          WT            1000000       NH: 150,  Z0: 0.03         1     0.01
        #   2     1          PV            2000000       NH: 0,    Z0: {}           2     0.02
        #   3     2          WT            3000000       NH: 200,  Z0: 0.2          3     0.03
        #   4     1          PV            4000000       NH: 0,    Z0: {}           4     0.04
        #   5     2          WT            5000000       NH: 250,  Z0: 0.03         5     0.05
        #   6     1          PV            6000000       NH: 0,    Z0: {}           6     0.06
        #   8     3        OTHER           1000000       NH: 0,    Z0: {}           7     0.07
        #   10    3        OTHER           1000000       NH: 0,    Z0: {}           8     0.08
        #   11    4        OTHER           1000000       NH: 0,    Z0: {}           9     0.09
        # [KWID, FKKWT, KWBezeichnung, Power, Weitere spezifische parameter(Nabenhoehe, Z0, usw.), Capex, Opex, KEV, Brennstoffkosten, Entsorgungskostne, CO2-Kosten, usw.]
        #
        # Output Arguments:
        # AuslastungAllerKWs: Dictionary containing KWIDs in the first column  and corresponding calculated
        # load(Auslastung) of a power plant in following 96 columns, output values are between [0-1] except KWIDs
        # -----------------
        # KWIDs  Auslastung   Note: Output matrix is not sorted and contains the load of wind turbines at first place
        # -----------------         on the top, then comes the load of PV and in the last comes the load of remaining
        #   1    array(96)          power plants(having 100% load).
        #   3    array(96)
        #   5    array(96)
        #   2    array(96)
        #   4    array(96)
        #   6    array(96)
        ###################################################################################################################

        WTauslastungID = np.array([WTauslastung['id']]).transpose()     #shape(3,1)
        WTauslastungLoad = WTauslastung['load']                         #shape(3,96)
        WTauslastung = np.hstack((WTauslastungID, WTauslastungLoad))

        PVauslastungID = np.array([PVauslastung['id']]).transpose()  # shape(3,1)
        PVauslastungLoad = PVauslastung['load']                      # shape(3,96)
        PVauslastung = np.hstack((PVauslastungID, PVauslastungLoad))

        LWKWauslastungID = np.array([LWKWauslastung['id']]).transpose()  # shape(3,1)
        LWKWauslastungLoad = LWKWauslastung['load']  # shape(3,96)
        LWKWauslastung = np.hstack((LWKWauslastungID, LWKWauslastungLoad))

        SWKWAuslastungID = np.array([SWKWAuslastung['id']]).transpose()  # shape(3,1)
        SWKWAuslastungLoad = SWKWAuslastung['load']  # shape(3,96)
        SWKWAuslastung = np.hstack((SWKWAuslastungID, SWKWAuslastungLoad))

        AuslastungWtPvLwSw = np.vstack((WTauslastung, PVauslastung, LWKWauslastung, SWKWAuslastung))

        # Filtering elements in KWDaten that are not in AuslastungWtPvLwSw, representing power plants other than PV,
        # Wind, Running-Water, or Storage
        # BoolDifference is a 1D vector holding TRUE/FALSE, False values corresponds to the values present only in KWDaten
        KWDatenID = np.array([KWDaten['id']]).transpose()  # shape(3,1)
        BoolDifference = np.in1d(KWDatenID[:, 0], AuslastungWtPvLwSw[:, 0])

        # Extracting KWIDs of other power plants
        OtherPowerPlantIDs = KWDatenID[BoolDifference == False]
        # 100% Auslastung =1
        AuslastungOPP = np.ones((OtherPowerPlantIDs.shape[0], len(WTauslastungLoad[0])))
        OtherPowerPlantsAuslastung = np.hstack((OtherPowerPlantIDs, AuslastungOPP))

        AuslastungAllerKWs = np.vstack((AuslastungWtPvLwSw, OtherPowerPlantsAuslastung))
        AuslastungAllerKWs = {'id': AuslastungAllerKWs[:,0].tolist(), 'load': AuslastungAllerKWs[:,1:].tolist()}
        return AuslastungAllerKWs

