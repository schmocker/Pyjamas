import asyncio
from pyjamas_core.util import Input, Output, Property
from pyjamas_core.supermodel import Supermodel

class Model(Supermodel):
    """Multiplies an input by a property number and outputs the result
    """

    def __init__(self, uuid, name :str):
        super(Model, self).__init__(uuid,name)

        self.inputs['number'] = Input('Number', unit='-', info="The number that gets multiplied", example='2')

        self.properties['multiplier'] = Property('Multiplier', default=1, data_type=float, unit='float', info='The multiplier', example='2')

        self.outputs['product'] = Output('Product', unit='-', info="The resulting product", example='2')

    async def func_peri(self, prep_to_peri=None):

        number = await self.get_input('number')
        multiplier = self.get_property('multiplier')

        product = number * multiplier

        self.set_output('product', product) 