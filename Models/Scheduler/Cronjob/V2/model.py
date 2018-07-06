import asyncio
from core.util import Input, Output, Property
from core.supermodel import Supermodel
import calendar as cal
import time

class Model(Supermodel):
    """
        schedules the func gates of the agent
        sets the number of elapsed rounds as output
    """

    def __init__(self, uuid, name: str):
        super(Model, self).__init__(uuid, name)

        self.step = 0
        self.time_of_curr_run = 0
        self.time_of_next_run = 0
        self.async_future = None

        self.outputs['step'] = Output('Step', unit='-', info='step number, starts with 0')
        self.outputs['times'] = Output('Futures', unit='s', info='utc time array in seconds since epoch')

        self.properties["future_steps"] = Property('Number of intervals', default=1, data_type=int,
                                                   unit='-',  info='Number of time stamps')
        self.properties["mode"] = Property('Mode', default='live', data_type=str,
                                           unit='-',
                                           info='live or simulation')
        self.properties["time_increase"] = Property('Time increase', default=1, data_type=float,
                                                    unit='s',
                                                    info='Time increase with each iteration')

        # Simulation
        self.properties["sim_speed"] = Property('Simulation speed', default=0, data_type=float, unit='s',
                                                info='Time between iteration, simulation mode only, 0 = as fast as possible')
        self.properties["sim_start"] = Property('Simulation Start (UTC)', default="2018-01-01 00:00", data_type=str,
                                                unit='YYYY-MM-DD hh:mm')

    async def func_birth(self):

        now = time.time()
        if self.get_property('mode') == 'live':
            self.time_of_curr_run = now
            self.time_of_next_run = now + self.get_property('time_increase') - (now % self.get_property('time_increase'))
        else:
            self.time_of_next_run = now
            try:
                start_time = cal.timegm(time.strptime(self.get_property('sim_start'), '%Y-%m-%d %H:%M'))
                self.time_of_curr_run = start_time
            except ValueError:
                self.log_error(f'property sim_start could not be converted to time format')
                self.agent.send_kill_order()

        self.close_gates()
        self.async_future = asyncio.ensure_future(self.loop())

    def close_gates(self):
        if self.get_property('time_increase') > 0:
            # print("closing peri gate")
            self.agent.peri_gate.clear()

    async def loop(self):
        while self.alive:

            if self.get_property('mode') == 'live':
                sleep_amount = self.time_of_next_run - time.time()
                
                self.time_of_next_run = self.time_of_next_run + self.get_property('time_increase')
            else:
                sim_speed = self.get_property('sim_speed')
                if sim_speed == 0:
                    sleep_amount = 0
                else:
                    sleep_amount = self.time_of_next_run - time.time()
                    self.time_of_next_run = self.time_of_next_run + sim_speed

            await asyncio.sleep(sleep_amount)

            # TODO: implement prep and post times according to peri time

            if not self.agent.peri_gate.is_set():
                # print("opening peri gate")
                self.agent.peri_gate.set()

    async def func_prep(self):

        self.set_output("step", self.model_run)

        steps = self.get_property("future_steps")
        if steps < 1:
            steps = 1
        interval = self.get_property("time_increase")

        if self.get_property('mode') == 'live':
            self.time_of_curr_run = self.time_of_next_run
            futures = [i * interval + self.time_of_curr_run for i in range(steps)]
            self.set_output("times", futures)
        
        else:
            time = self.time_of_curr_run
            futures = [i * interval + time for i in range(steps)]
            self.set_output("times", futures)
            self.time_of_curr_run += interval

    async def func_in_sync(self):
        self.close_gates()

    async def func_amend(self, keys=[]):
        if 'mode' in keys:
            self.async_future.cancel()
            await self.func_birth()
        if 'time_increase' in keys and self.get_property('mode') == 'live':
            now = time.time()
            self.time_of_curr_run = now
            self.time_of_next_run = now + self.get_property('time_increase') - (now % self.get_property('time_increase'))
            self.async_future.cancel()
            self.async_future = asyncio.ensure_future(self.loop())