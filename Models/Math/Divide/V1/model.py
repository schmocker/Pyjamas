import asyncio
from core.util import Input, Output, Property
from core.supermodel import Supermodel

class Model(Supermodel):
    """
        divides the input and delivers several outputs

        WARNING: this model was created for test purposes and does not garantee the correctness of the results
    """

    def __init__(self, uuid, name :str):
        super(Model, self).__init__(uuid,name)

        self.inputs['dividend'] = Input({'name': 'Dividend', 'unit': 'num', 'dimensions': []})
        self.inputs['divisor'] = Input({'name': 'Divisor', 'unit': 'num', 'dimensions': []})

        self.outputs['quotient'] = Output({'name': 'Quotient', 'unit': 'num', 'dimensions': []})
        self.outputs['floor_quotient'] = Output({'name': 'Floor Quotient', 'unit': 'num', 'dimensions': []})
        self.outputs['floor_modulus'] = Output({'name': 'Floor Modulus', 'unit': 'num', 'dimensions': []})

    async def func_peri(self, prep_to_peri=None):

        dividend = await self.get_input('dividend')
        divisor = await self.get_input('divisor')

        if divisor == 0:
            self.set_output("quotient",float("inf"))
            self.set_output("floor_quotient",float("inf"))
            self.set_output("floor_modulus",float("inf"))
        else:
            quot = dividend / divisor
            self.set_output("quotient",quot)

            f_quot = dividend // divisor
            self.set_output("floor_quotient",f_quot)

            f_mod = dividend % divisor
            self.set_output("floor_modulus",f_mod)

        