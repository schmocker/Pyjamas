# imports for core
from core import Supermodel
from core.util import Input, Output, Property

# import for timing
import datetime

# used for interpolating
import numpy as np


# define the model class and inherit from class "Supermodel"
class Model(Supermodel):
    # model constructor
    def __init__(self, id, name: str):
        # instantiate supermodel
        super(Model, self).__init__(id, name)

        # define outputs
        self.outputs['t'] = Output({'name': 'Zeitarray'})

        # define properties
        self.properties['dt'] = Property(900, {'name': 'Zeitschritt [s]'})

    async def func_birth(self):
        pass

    async def func_amend(self, keys=[]):
        pass

    async def func_prep(self):
        dt = self.get_property('dt')
        t0 = datetime.datetime.now()
        t = t0 + np.arange(96) * datetime.timedelta(seconds=dt)
        # equivalent, unused
        # t = np.array([t0 + datetime.timedelta(seconds=dt) * i for i in range(96)])

        return t

    async def func_peri(self, prep_to_peri=None):
        t_out = prep_to_peri

        # set output
        self.set_output("t", t_out)

        break1 = 0

    async def func_post(self, peri_to_post=None):
        pass

    async def func_death(self):
        print("I am dying! Bye bye!")


if __name__ == "__main__":
    dt = 100
    properties = {'dt': dt}

    outputs = Model.test(inputs, properties)

