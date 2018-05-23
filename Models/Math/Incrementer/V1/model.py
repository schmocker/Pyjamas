import asyncio
from core.supermodel import Supermodel

class Model(Supermodel):
    """
        sets a number as output that gets incremented each round
    """


    def __init__(self, uuid, name :str):
        super(Model,self).__init__(uuid,name,["num"])
        self.number = -1

        ##########
       #self.input.add('auslastung','Auslastung',0,'%',dim=['Zeit','Kraftwerk'])

       #self.inputs['auslastung'] = {'name': 'Auslastung', 'value': 0, 'unit': '%', 'dimensions': ['Zeit','Kraftwerk']}
       #self.inputs['hoehe'] = {'name': 'Höhe', }
       #self.outputs['leistung'] = {'name': 'Leistung', }
       #self.properties['wirkungsgrad'] = {'name': 'Leistung', }


    async def func_prep(self):
        self.number = self.number + 1

    async def func_peri(self, prep_to_peri=None):
        self.set_output("num",self.number)

        ##########
        #ausl = await self.inputs.get('auslastung')
#
        #ausl = await self.get_input('auslastung')
        #hoehe = await self.get_input('hoehe')
        #leistung = ausl * hoehe
        #self.set_output('leistung',leistung)

######
#class Port:
#    def __init__(self):
#        pass
#
#    async def get(self,port_name):
#        result await ...
#
#        # controlle
#
#        return result

