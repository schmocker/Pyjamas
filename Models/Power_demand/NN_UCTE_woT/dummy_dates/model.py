from core import Supermodel
from core.util import Input, Output, Property
from datetime import datetime, timedelta
import pytz
import numpy as np

# define the model class and inherit from class "Supermodel"
class Model(Supermodel):
    # model constructor
    def __init__(self, id, name: str):
        # instantiate supermodel
        super(Model, self).__init__(id, name)

        # define outputs
        self.outputs['dates'] = Output({'name': 'dates'})


    async def func_peri(self, prep_to_peri=None):

        dates = [datetime(2006, 1, d, 1, 0) for d in [1, 2, 3]]

        # set output
        self.set_output("dates", dates)
