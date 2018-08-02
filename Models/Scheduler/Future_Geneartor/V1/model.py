import asyncio
from core.util import Input, Output, Property
from core.supermodel import Supermodel
import numpy as np


class Model(Supermodel):
    """
        takes a time as input and sets a list of times as output
    """

    def __init__(self, uuid, name: str):
        super(Model, self).__init__(uuid,name)
        self.elapsed = 0

        self.inputs['time'] = Input(name='Time', unit='s', info='utc time in seconds since epoch')

        self.outputs['times'] = Output(name='Futures', unit='s', info='utc time array in seconds since epoch')

        self.properties["interval"] = Property(default=1, data_type=float, name='Interval time',
                                               unit='s',  info='Time between each time stamps')
        self.properties["future_steps"] = Property(default=1, data_type=int, name='Number of intervals',
                                                   unit='-',  info='Number of time stamps')

    async def func_peri(self, prep_to_peri=None):
        time = await self.get_input("time")
        steps = self.get_property("future_steps")
        if steps < 1:
            steps = 1
        interval = self.get_property("interval")
        futures = [i * interval + time for i in range(steps)]
        self.set_output("times", futures)
