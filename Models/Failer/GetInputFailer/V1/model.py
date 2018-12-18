from pyjamas_core.util import Input, Output, Property
from pyjamas_core.supermodel import Supermodel


class Model(Supermodel):
    def __init__(self, uuid, name: str):
        super(Model, self).__init__(uuid, name)


    async def func_peri(self, prep_to_peri=None):
        #this should fail here and stop the simulation
        await self.get_input('input_that_does_not_exist')


if __name__=='__main__':
    inputs = {}
    properties = {}
    outputs = Model.test(inputs, properties)
    print(outputs)
