from core import Supermodel
from core.util import Input, Output, Property

from flask import Markup
import markdown2
import os
from pathlib import Path

import json
from .NN_prepfunc import prep_date
from .NN_functions import func_NeuralNetwork

# define the model class and inherit from class "Supermodel"
class Model(Supermodel):
    # model constructor
    def __init__(self, id, name: str):
        # instantiate supermodel
        super(Model, self).__init__(id, name)

        # define inputs
        self.inputs['date'] = Input({'name': 'date'})

        # define outputs
        self.outputs['p_dem'] = Output({'name': 'power demand'})

        # define properties
        self.properties['offset'] = Property(10,float, {'name': 'demand offset'})

        # define persistent variables
        self.model_pars = None

    async def func_birth(self):
        # listA = [1,2,3,4] #array
        # dictA = {'alter': 5, 'grösse': 1.2}
        # gr = dictA["grösse"]

        filepath = "model_parameter_LK_UCTE.txt"
        with open(filepath, 'r') as f:
            json_str = f.read()
            data = json.loads(json_str)

        self.model_para = json.loads(json_str)


    async def func_peri(self, prep_to_peri=None):
        # get inputs
        dates = await self.get_input('date')

        # date preparation
        #prep_date(self, date_i='01.01.2006 01:00', country_i=1)
        NN_input = prep_date()

        # calculations
        demand = func_NeuralNetwork(NN_input)

        # set output
        self.set_output("p_dem", demand)
