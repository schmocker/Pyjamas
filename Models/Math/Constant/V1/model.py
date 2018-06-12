import asyncio
from core.util import Input, Output, Property
from core.supermodel import Supermodel

class Model(Supermodel):
    """
        sets a constant number as output
    """

    def __init__(self, uuid, name :str):
        super(Model,self).__init__(uuid,name)
        self.outputs['const'] = Output({'name': 'Number', 'unit': 'int', 'dimensions': []})
        
        self.properties['number'] = Property(0,float, {'name': 'Number', 'unit': 'int', 'dimensions': []})


    async def func_peri(self, prep_to_peri=None):

        num = self.get_property('number')

        self.set_output("const",num)