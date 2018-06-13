from core import Supermodel
from core.util import Input, Output, Property
from datetime import datetime


# define the model class and inherit from class "Supermodel"
class Model(Supermodel):
    # model constructor
    def __init__(self, id, name: str):
        # instantiate supermodel
        super(Model, self).__init__(id, name)

        # define outputs
        self.outputs['dates'] = Output({'name': 'dates'})


    async def func_peri(self, prep_to_peri=None):
        date_list = ['01.01.2006 01:00', '01.01.2006 02:00', '01.01.2006 03:00', '01.01.2006 04:00']
        dates = [datetime.strptime(x, '%d.%m.%Y %H:%M') for x in date_list]
        # set output
        self.set_output("dates", dates)