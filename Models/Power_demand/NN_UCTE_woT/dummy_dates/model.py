from core import Supermodel
from core.util import Input, Output
from datetime import datetime, timedelta
from Models._utils.time import datetime2utc_time

# define the model class and inherit from class "Supermodel"
class Model(Supermodel):
    # model constructor
    def __init__(self, id, name: str):
        # instantiate supermodel
        super(Model, self).__init__(id, name)

#        self.inputs['step'] = Input({'Name': 'step'})
        self.inputs['step'] = Input(name='step')

        # define outputs
        self.outputs['dates'] = Output(name='dates')


    async def func_peri(self, prep_to_peri=None):

        start_datetime = datetime(2006, 1, 1, 1, 0)
        # step = 0
        step = await self.get_input('step')
        time_deltas = [timedelta(seconds=(x + step)*60*15) for x in [0, 1, 2, 3]]
        dates = [start_datetime + time_delta for time_delta in time_deltas]
        print(dates)
        dates = [datetime2utc_time(x) for x in dates]
        # print(dates)

        # set output
        # set output
        self.set_output("dates", dates)
