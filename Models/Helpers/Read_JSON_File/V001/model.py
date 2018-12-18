from pyjamas_core import Supermodel
from pyjamas_core.util import Input, Output, Property
import os
import json

class Model(Supermodel):
    # model constructor
    def __init__(self, model_id, name: str):
        # instantiate supermodel
        super(Model, self).__init__(model_id, name)

        # define inputs
        self.outputs['data'] = Output({'name': 'Data'})

        # define persistent variables
        self.data = None

    async def func_birth(self):
        path = os.path.dirname(os.path.realpath(__file__))
        file = "model_parameter_LK_UCTE.txt"
        filepath = os.path.join(path, file)
        try:
            with open(filepath, 'r') as f:
                f = open(filepath, 'r')
                json_str = f.read()
                data = json.loads(json_str)
        except Exception as e:
            print(e)
            data = None
        self.data = data


    async def func_peri(self, prep_to_peri=None):
        self.set_output("data", self.data)