import asyncio
from core.util import Output, Property
from core.supermodel import Supermodel
import time
from Models import utc_time2datetime
import calendar as cal

class Model(Supermodel):
    """
        schedules the func gates of the agent
        sets the number of elapsed rounds as output
    """

    def __init__(self, uuid, name: str):
        super(Model, self).__init__(uuid, name)
        self.step = 0
        self.current_time = 0
        self.future = 0
        self.async_future = None

        self.outputs['time'] = Output(name='Time', unit='s', info='utc time in seconds since epoch')
        self.outputs['step'] = Output(name='Step', unit='-', info='step number, starts with 0')

        self.properties["mode"] = Property('live', str,
                                           name='Mode',
                                           unit='-',
                                           info='live or simulation')
        self.properties["time_increase"] = Property(1, float,
                                                    name='Time increase',
                                                    unit='s',
                                                    info='Time increase with each iteration')
        # Live
        # Simulation
        self.properties["sim_speed"] = Property(0, float, name='Simulation speed', unit='s',
                                                info='Time between iteration, simulation mode only, 0 = as fast as possible')
        self.properties["sim_start"] = Property("2018-01-01 00:00", str,
                                                name='Simulation Start (UTC)',
                                                unit='YYYY-MM-DD hh:mm')

    async def func_birth(self):

        sim_start = cal.timegm(time.strptime(self.get_property("sim_start"), '%Y-%m-%d %H:%M'))
        print(utc_time2datetime(sim_start))

        now = time.time()

        self.future = now + self.get_property('time_increase') - (now % self.get_property('time_increase'))

        self.close_gates()
        self.async_future = asyncio.ensure_future(self.loop())


    async def func_amend(self, keys=[]):
        if "time_increase" in keys:
            self.future = self.current_time + self.get_property('time_increase') - (self.current_time % self.get_property('time_increase'))
            self.async_future.cancel()
            self.async_future = asyncio.ensure_future(self.loop())


    async def func_prep(self):

        self.set_output("step", self.step)
        self.step = self.step + 1
        self.current_time = self.future
        self.set_output("time", self.current_time)

    async def func_post(self, peri_to_post=None):
        pass

    async def func_in_sync(self):
        self.close_gates()

    def close_gates(self):
        if self.get_property('time_increase') > 0:
            print("closing peri gate")
            self.agent.peri_gate.clear()

    async def loop(self):

        while True:
            await asyncio.sleep(self.future - time.time())
            self.future = self.future + self.get_property('time_increase')
            if not self.agent.peri_gate.is_set():
                print("opening peri gate")
                self.agent.peri_gate.set()
