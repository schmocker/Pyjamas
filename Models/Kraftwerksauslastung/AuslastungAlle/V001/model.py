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
        self.inputs['WTAuslastung'] = Input(name='LoadWT')
        self.inputs['PVAuslastung'] = Input(name='LoadPV')
        self.inputs['KWDaten'] = Input(name='PowerPlantsData')

        # define outputs
        self.outputs['GemeinsameAuslastung'] = Output(name='CombinedLoad')

    async def func_peri(self, prep_to_peri=None):
        # get inputs
        WTAuslastung = await self.get_input('WTAuslastung')
        PVAuslastung = await self.get_input('PVAuslastung')
        KWDaten = await self.get_input('KWDaten')

        # calculate
        GemeinsameAuslastung = self.auslastungallerKWs(WTAuslastung, PVAuslastung, KWDaten)

        # set output
        self.set_output("GemeinsameAuslastung", GemeinsameAuslastung)


    # define additional methods (normal)
    def auslastungallerKWs(self, WTauslastung, PVauslastung, KWDaten):
        # Determine the loading(Auslastung) of each power plant according to incoming Foreign Keys separately and then
        # combine them together in a matrix to form combined loading
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
        # Output Arguments:
        # GemeinsameAuslastungAllerKWs: Matrix containing KWIDs in the first column  and corresponding calculated
        # loading(Auslastung) of a power plant in following 96 columns, output values are between [0-1] except KWIDs
        # -----------------
        # KWIDs  Auslastung   Note: Output matrix is not sorted according to incoming KWIDs, will be done if required
        # -----------------
        #   1    array(96)
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

        AuslastungWTundPV = np.vstack((WTauslastung, PVauslastung))

        # Filtering elements in KWDaten that are not in AuslastungWTundPV, representing power plants other than PV or Wind
        # BoolDifference is a 1D vector holding TRUE/FALSE, False values corresponds to the values present only in KWDaten
        KWDatenID = np.array([KWDaten['id']]).transpose()  # shape(3,1)
        BoolDifference = np.in1d(KWDatenID[:, 0], AuslastungWTundPV[:, 0])

        # Extracting KWIDs of other power plants
        OtherPowerPlantIDs = KWDatenID[BoolDifference == False]
        # 100% Auslastung =1
        AuslastungOPP = np.ones((OtherPowerPlantIDs.shape[0], 96))
        OtherPowerPlantsAuslastung = np.hstack((OtherPowerPlantIDs, AuslastungOPP))

        AuslastungAllerKWs = np.vstack((AuslastungWTundPV, OtherPowerPlantsAuslastung))
        AuslastungAllerKWs = {'id': AuslastungAllerKWs[:,0].tolist(), 'load': AuslastungAllerKWs[:,1:].tolist()}
        return AuslastungAllerKWs

