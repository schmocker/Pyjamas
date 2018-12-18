import asyncio
from pyjamas_core.util import Input, Output, Property
from pyjamas_core.supermodel import Supermodel
import calendar as cal
import time

class Model(Supermodel):
    """
        schedules the func gates of the agent
        sets the number of elapsed rounds as output
    """

    def __init__(self, uuid, name: str):
        super(Model, self).__init__(uuid, name)

        self.start_time_of_curr_interval = 0
        self.start_time_of_next_interval = 0
        self.simulation_time = 0
        self.async_future = None

        self.outputs['step'] = Output('Step', unit='-', info='step number, starts with 0')
        self.outputs['time'] = Output('Future', unit='s', info='utc time in seconds since epoch')

        # control
        self.properties['prep_lead'] = Property('Time lead of Preperation step', default=0, data_type=int, unit='s', info='Amount of seconds the preparation step is started before the actual interval')
        self.properties['sim_speed'] = Property('Simulation speed', default=1, data_type=int, unit='s', info='Seconds between simulation runs, 0 = as fast as possible')

        # Simulation
        self.properties['date_start'] = Property('Simulation Start (UTC)', default="2018-01-01 00:00", data_type=str, unit='YYYY-MM-DD hh:mm')
        self.properties['date_delta_time'] = Property('Simulation time increase', default=1, data_type=float, unit='s', info='Amount of seconds the simulation time increases with each iteration')
        self.properties['date_end'] = Property('Simulation Stop (UTC)', default="2999-01-01 00:00", data_type=str, unit='YYYY-MM-DD hh:mm')
 
    async def func_birth(self):
        # set simulation_time and start_time_of_next_interval

        now = time.time()

        sim_speed = self.get_property('sim_speed')
        date_start_string = self.get_property('date_start')

        if date_start_string != '':
            try:
                date_start = cal.timegm(time.strptime(date_start_string, '%Y-%m-%d %H:%M'))
                self.start_time_of_next_interval = now
                self.simulation_time = date_start
            except ValueError:
                self.log_error(f'property date_start could not be converted to time format')
                self.agent.send_kill_order()

        else:
            self.start_time_of_next_interval = now + sim_speed - (now % sim_speed)
            self.simulation_time = self.start_time_of_next_interval

        self.close_gates()
        self.async_future = asyncio.ensure_future(self.loop())

    def close_gates(self):
        if self.get_property('sim_speed') > 0:
            self.agent.peri_gate.clear()
        if self.get_property('prep_lead') > 0:
            self.agent.prep_gate.clear()

    async def loop(self):
        while self.alive:
            time_increase = self.get_property('sim_speed')
            prep_lead = self.get_property('prep_lead')

            if time_increase <= 0:
                time_increase = 0
                prep_lead = 0
                now = time.time()
                self.start_time_of_curr_interval = now
                self.start_time_of_next_interval = now
                await asyncio.sleep(0)
            else:

                if prep_lead > 0:
                    prep_sleep_amount = self.start_time_of_next_interval - prep_lead - time.time()
                    if prep_sleep_amount < 0:
                        prep_sleep_amount = 0
                    await asyncio.sleep(prep_sleep_amount)
                    if not self.agent.prep_gate.is_set():
                        self.agent.prep_gate.set()

                sleep_amount = self.start_time_of_next_interval - time.time()
                await asyncio.sleep(sleep_amount)

                time_increase = self.get_property('sim_speed')
                if time_increase <= 0:
                    time_increase = 0
                    now = time.time()
                    self.start_time_of_curr_interval = now
                    self.start_time_of_next_interval = now
                else:
                    self.start_time_of_curr_interval = self.start_time_of_next_interval
                    self.start_time_of_next_interval = self.start_time_of_next_interval + time_increase

            if not self.agent.prep_gate.is_set():
                self.agent.prep_gate.set()
            if not self.agent.peri_gate.is_set():
                self.agent.peri_gate.set()

    async def func_prep(self):

        self.set_output("step", self.model_run)

        date_delta_time = self.get_property('date_delta_time')

        self.set_output("time", self.simulation_time)
        self.simulation_time += date_delta_time

    async def func_in_sync(self):

        date_end_string = self.get_property('date_end')
        try:
            date_end = cal.timegm(time.strptime(date_end_string, '%Y-%m-%d %H:%M'))
        except ValueError:
            self.log_error(f'property date_start could not be converted to time format')
            date_end = 0

        if date_end != 0 and date_end < self.simulation_time:
            self.agent.end_all_model_loops()
        else:
            self.close_gates()

    async def func_amend(self, keys=[]):
        if 'date_start' in keys:
            self.async_future.cancel()
            await self.func_birth()