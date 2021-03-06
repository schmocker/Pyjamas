import asyncio
from pyjamas_core.util import Input, Output, Property
from pyjamas_core.supermodel import Supermodel

class Model(Supermodel):
    """
        sets a constant number as output
    """

    def __init__(self, uuid, name :str):
        super(Model,self).__init__(uuid,name)
        self.outputs['const1'] = Output({'name': 'Number1', 'unit': 'int', 'dimensions': []})
        self.outputs['const2'] = Output({'name': 'Number2', 'unit': 'int', 'dimensions': []})

        self.properties['number1'] = Property(default=0, data_type=float, name='Number 1', unit='-')
        self.properties['number2'] = Property(default=0, data_type=float, name='Number 2', unit='-')

    async def func_peri(self, prep_to_peri=None):

        num = self.get_property('number1')
        self.set_output("const1", num)

        num = self.get_property('number2')
        self.set_output("const2", num)
