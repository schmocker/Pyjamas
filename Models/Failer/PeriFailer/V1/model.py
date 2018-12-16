from pyjamas_core.util import Input, Output, Property
from pyjamas_core.supermodel import Supermodel


class Model(Supermodel):
    def __init__(self, uuid, name: str):
        super(Model, self).__init__(uuid, name)

    async def func_peri(self, prep_to_peri=None):
        raise Exception('Test Exception')


if __name__=='__main__':
    inputs = {}
    properties = {}
    outputs = Model.test(inputs, properties)
    print(outputs)
