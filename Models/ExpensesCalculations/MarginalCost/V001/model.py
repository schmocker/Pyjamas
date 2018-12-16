from pyjamas_core import Supermodel
from pyjamas_core.util import Input, Output


# define the model class and inherit from class "Supermodel"
class Model(Supermodel):
    # model constructor
    def __init__(self, model_id, name: str):
        # instantiate supermodel
        super(Model, self).__init__(model_id, name)

        # define inputs
        self.inputs['KWDaten'] = Input('PowerPlantsData', unit='[€/J]', info='complete power plant information')

        # define outputs
        self.outputs['Grenzkosten'] = Output('MarginalCost', unit='[€/J]')

    async def func_peri(self, prep_to_peri=None):
        # get inputs
        kw_daten = await self.get_input('KWDaten')

        idx = kw_daten['id']
        opex = kw_daten['var_opex']
        bs_kosten = kw_daten['brennstoffkosten']
        co2_kosten = kw_daten['co2_kosten']
        ents_kosten = kw_daten['entsorgungskosten']

        # add lists elementwise
        marg_cost = [a+b+c+d for a, b, c, d in zip(opex, bs_kosten, co2_kosten, ents_kosten)]
        # assemble output dict
        out = {'power_plant_id': idx, 'MarginalCost': marg_cost}
        # set output
        self.set_output("Grenzkosten", out)
