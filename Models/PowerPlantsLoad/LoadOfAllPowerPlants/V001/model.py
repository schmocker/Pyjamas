from pyjamas_core import Supermodel
from pyjamas_core.util import Input, Output, Property
import numpy as np

# define the model class and inherit from class "Supermodel"
class Model(Supermodel):
    # model constructor
    def __init__(self, id, name: str):
        # instantiate supermodel
        super(Model, self).__init__(id, name)

        # define inputs
        self.inputs['WTAuslastung'] = Input('LoadWindTurbine', info='load of all wind turbines, value[0-1]')
        self.inputs['PVAuslastung'] = Input('LoadPhotovoltaic', info='load of all photovoltaic power plants, value[0-1]')
        self.inputs['LaufwasserKWAuslastung'] = Input('LoadRunningWaterPowerPlant', info='load of all running-water power plants, value[0-1]')
        self.inputs['SpeicherwasserKWAuslastung'] = Input('LoadStoragePowerPlant', info='load of all storage power plants, value[0-1]')
        self.inputs['KWDaten'] = Input('PowerPlantsData', info='dict, power plant id required')
        self.inputs['futures'] = Input('Futures', unit='s', info='utc time array in seconds since epoch')

        # define outputs
        self.outputs['GemeinsameAuslastung'] = Output('CombinedLoad', info='combined load of all types of power plants, value[0-1]')

    async def func_peri(self, prep_to_peri=None):
        # get inputs
        WTAuslastung = await self.get_input('WTAuslastung')
        PVAuslastung = await self.get_input('PVAuslastung')
        LWKWAuslastung = await self.get_input('LaufwasserKWAuslastung')
        SWKWAuslastung = await self.get_input('SpeicherwasserKWAuslastung')
        KWDaten = await self.get_input('KWDaten')
        Futures = await self.get_input('futures')

        # calculate
        GemeinsameAuslastung = self.auslastungallerKWs(WTAuslastung, PVAuslastung, LWKWAuslastung, SWKWAuslastung, KWDaten, Futures)

        # set output
        self.set_output("GemeinsameAuslastung", GemeinsameAuslastung)


    # define additional methods (normal)
    def auslastungallerKWs(self, WTauslastung, PVauslastung, LWKWauslastung, SWKWauslastung, KWDaten, Futures):
        # Determine the load(Auslastung) of each power plant according to incoming power plant key
        # separately and then combine them together to form combined load
        ###################################################################################################################
        # Input Arguments:
        ## WTauslastung: Dictionary containing Power plant IDs(id) in the first list and corresponding calculated
        # load(Auslastung) of wind turbines in second list, output values are between [0-1] except ids
        # -----------------
        #   id  Auslastung   Note: Input matrix contains the load of wind turbines only
        # -----------------
        #   2    array(96)
        #   4    array(96)
        #   6    array(96)
        #
        # PVauslastung: Dictionary containing Power plant IDs(id) in the first list and corresponding calculated
        # load(Auslastung) of photovoltaic power plants in second list, output values are between [0-1] except ids
        # -----------------
        #   id  Auslastung   Note: Input matrix contains the load of PV power plants only
        # -----------------
        #   2    array(96)
        #   4    array(96)
        #   6    array(96)
        #
        # LWKWauslastung: Dictionary containing Power plant IDs(id) in the first list and corresponding calculated
        # load(Auslastung) of running-water power plants in second list, output values are between [0-1] except ids
        # -----------------
        #   id  Auslastung   Note: Input matrix contains the load of running-water power plants only
        # -----------------
        #   10    array(96)
        #   11    array(96)
        #
        # SWKWauslastung: Dictionary containing Power plant IDs(id) in the first list and corresponding calculated
        # load(Auslastung) of storage power plants in second list, output values are between [0-1] except ids
        # -----------------
        #   id  Auslastung   Note: Input matrix contains the load of storage power plants only
        # -----------------
        #   10    array(96)
        #   11    array(96)
        #
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
        # Futures: Incoming datetime values (produced by Scheduler/Cronjob/V2)
        #
        # Output Arguments:
        # AuslastungAllerKWs: Dictionary containing Power plant IDs(id) in the first list and corresponding calculated
        # load(Auslastung) of all power plants in second list, output values are between [0-1] except ids
        # -----------------
        #   id  Auslastung   Note: Output dictionary is not sorted and contains the load of wind turbines at first place
        # -----------------        on the top, then comes the load of PV, running-water, and storage power plants
        #   1    array(96)         respectively, in the last comes the load of remaining power plants(having 100% load).
        #   3    array(96)
        #   5    array(96)
        #   2    array(96)
        #   4    array(96)
        #   6    array(96)
        ###################################################################################################################

        KWDatenID = KWDaten['id']
        WTids = WTauslastung['power_plant_id']
        PVids = PVauslastung['power_plant_id']
        LWKWids = LWKWauslastung['power_plant_id']
        SWKWids = SWKWauslastung['power_plant_id']
        ids = []
        load = []

        def make_load_for_one_plant(kw_id):
            if kw_id in WTids:
                ids.append(kw_id)
                index_of_kwid_in_WTauslastung = WTauslastung['power_plant_id'].index(kw_id)
                auslastung_for_kwid = WTauslastung['load'][index_of_kwid_in_WTauslastung]
                load.append(auslastung_for_kwid)
            elif kw_id in PVids:
                ids.append(kw_id)
                index_of_kwid_in_PVauslastung = PVauslastung['power_plant_id'].index(kw_id)
                auslastung_for_kwid = PVauslastung['load'][index_of_kwid_in_PVauslastung]
                load.append(auslastung_for_kwid)
            elif kw_id in LWKWids:
                ids.append(kw_id)
                index_of_kwid_in_LWKWauslastung = LWKWauslastung['power_plant_id'].index(kw_id)
                auslastung_for_kwid = LWKWauslastung['load'][index_of_kwid_in_LWKWauslastung]
                load.append(auslastung_for_kwid)
            elif kw_id in SWKWids:
                ids.append(kw_id)
                index_of_kwid_in_SWKWauslastung = SWKWauslastung['power_plant_id'].index(kw_id)
                auslastung_for_kwid = SWKWauslastung['load'][index_of_kwid_in_SWKWauslastung]
                load.append(auslastung_for_kwid)

            return

        [make_load_for_one_plant(id) for id in KWDatenID]


        def find_ids_of_other_powerplant(kwid):
            if kwid in ids:
                pass
            else:
                ids.append(kwid)
                load.append([1]*len(Futures))
            return

        [find_ids_of_other_powerplant(id) for id in KWDatenID]


        AuslastungAllerKWs = {'power_plant_id': ids, 'load': load}
        return AuslastungAllerKWs


    '''
        WTids = WTauslastung['id']
        PVids = PVauslastung['id']
        LWKWids = LWKWauslastung['id']
        SWKWids = SWKWauslastung['id']

        if not WTids:  # if WTids == []
            noWT = True
        else:
            WTauslastungID = np.array([WTauslastung['id']]).transpose()     #shape(3,1)
            WTauslastungLoad = WTauslastung['load']                         #shape(3,96)
            WTauslastung = np.hstack((WTauslastungID, WTauslastungLoad))

        if not PVids:   # if PVids == []
            noPV = True
        else:
            PVauslastungID = np.array([PVauslastung['id']]).transpose()  # shape(3,1)
            PVauslastungLoad = PVauslastung['load']                      # shape(3,96)
            PVauslastung = np.hstack((PVauslastungID, PVauslastungLoad))

        if not LWKWids:
            noLWKW = True
        else:
            LWKWauslastungID = np.array([LWKWauslastung['id']]).transpose()  # shape(3,1)
            LWKWauslastungLoad = LWKWauslastung['load']  # shape(3,96)
            LWKWauslastung = np.hstack((LWKWauslastungID, LWKWauslastungLoad))

        if not SWKWids:
            noSWKW = True
        else:
            SWKWAuslastungID = np.array([SWKWauslastung['id']]).transpose()  # shape(3,1)
            SWKWAuslastungLoad = SWKWauslastung['load']  # shape(3,96)
            SWKWAuslastung = np.hstack((SWKWAuslastungID, SWKWAuslastungLoad))

        if noPV:
            AuslastungWtPvLwSw = np.vstack((WTauslastung, LWKWauslastung, SWKWAuslastung))
        elif noWT:
            AuslastungWtPvLwSw = np.vstack((PVauslastung, LWKWauslastung, SWKWAuslastung))
        else:
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
    '''
