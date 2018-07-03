import asyncio
from core.util import Input, Output, Property
from core.supermodel import Supermodel

class Model(Supermodel):
    """
        sets the sum of 3 inputs as output
    """

    def __init__(self, uuid, name :str):
        super(Model, self).__init__(uuid,name)

        self.inputs['in1'] = Input(name='Number', unit='num')
        self.inputs['in2'] = Input(name='Number', unit='num')
        self.inputs['in3'] = Input(name='Number', unit='num')

        self.outputs['sum'] = Output(name='Sum', unit='num')


    async def func_peri(self, prep_to_peri=None):

        in1 = await self.get_input('in1')
        in2 = await self.get_input('in2')
        in3 = await self.get_input('in3')
        
        res = in1 + in2 + in3

        self.set_output("sum",res)

if __name__=='__main__':
    inputs = {
        'in1':1,
        'in2':2,
        'in3':3
    }

    properties = {}

    outputs = Model.test(inputs,properties)

    print(outputs)