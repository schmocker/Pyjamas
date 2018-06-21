import asyncio
from core.util import Input, Output, Property
from core.supermodel import Supermodel
import numpy as np

class Model(Supermodel):
    """
        schedules the func gates of the agent
        sets the number of elapsed rounds as output
    """

    def __init__(self, uuid, name: str):
        super(Model, self).__init__(uuid,name)
        self.elapsed = 0

        self.inputs['time'] = Input({'name': 'Time', 'unit': 'utc time', 'dimensions': []})

        self.outputs['times'] = Output({'name': 'Futures', 'unit': 'utc time array', 'dimensions': []})

        self.properties["interval"] = Property(1, float, {'name': 'Interval time', 'unit': 's', 'dimensions': []})
        self.properties["future_steps"] = Property(0, int, {'name': 'Number of intervals', 'unit': '-', 'dimensions': []})

    async def func_birth(self):
        pass

    async def func_prep(self):
        pass

    async def func_peri(self, prep_to_peri=None):
        time = await self.get_input("time")
        steps = self.get_property("future_steps")
        if steps < 1:
            steps = 1
        interval = self.get_property("interval")
        futures = (np.arange(steps) * interval + time).tolist()
        self.set_output("times", futures)

    async def func_post(self, peri_to_post=None):
        pass
