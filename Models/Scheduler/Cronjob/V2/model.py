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

        self.outputs['is_live'] = Output('Is live', info='True if the current mode is live')
        self.outputs['step'] = Output('Step', unit='-', info='step number, starts with 0')
        self.outputs['times'] = Output('Futures', unit='s', info='utc time array in seconds since epoch')

        self.properties['mode'] = Property('Mode', default='live', data_type=str, unit='-', info='live or simulation')

        # control
        self.properties['prep_lead'] = Property('Time lead of Preperation step', default=0, data_type=int, unit='s', info='Amount of seconds the preparation step is started before the actual interval')
        self.properties['real_time_increase'] = Property('Real time between each interval run', default=1, data_type=int, unit='s', info='Real time between iteration, 0 = as fast as possible')

        # Simulation
        self.properties['simu_time_increase'] = Property('Simulation time increase', default=1, data_type=float, unit='s', info='Amount of seconds the simulation time increases with each iteration')
        self.properties['simu_start_time'] = Property('Simulation Start (UTC)', default="2018-01-01 00:00", data_type=str, unit='YYYY-MM-DD hh:mm')

        # futures
        self.properties['future_steps_amount'] = Property('Number of Future steps', default=1, data_type=int, unit='-',  info='Number of time stamps')
        self.properties['future_time_increase'] = Property('Time increase with each Future', default=0, data_type=float, unit='s', info='Time increase with each iteration')

        # stop
        self.properties['simu_stop_time'] = Property('Simulation Stop (UTC)', default="2999-01-01 00:00", data_type=str, unit='YYYY-MM-DD hh:mm')
        self.properties['simu_number_of_intervals'] = Property('Number of Simulation intervals', default=-1, data_type=int)

    async def func_birth(self):
        # set simulation_time and start_time_of_next_interval

        now = time.time()

        mode = self.get_property('mode')
        real_time_increase = self.get_property('real_time_increase')
        simu_start_time_string = self.get_property('simu_start_time')

        if mode == 'live':

            if simu_start_time_string != '':
                try:
                    simu_start_time = cal.timegm(time.strptime(simu_start_time_string, '%Y-%m-%d %H:%M'))
                    self.start_time_of_next_interval = simu_start_time
                    self.simulation_time = self.start_time_of_next_interval
                except ValueError:
                    self.log_error(f'property simu_start_time could not be converted to time format')
                    self.agent.send_kill_order()                

            else:
                self.start_time_of_next_interval = now + real_time_increase - (now % real_time_increase)
                self.simulation_time = self.start_time_of_next_interval
        else:

            if simu_start_time_string != '':
                try:
                    simu_start_time = cal.timegm(time.strptime(simu_start_time_string, '%Y-%m-%d %H:%M'))
                    self.start_time_of_next_interval = now
                    self.simulation_time = simu_start_time
                except ValueError:
                    self.log_error(f'property simu_start_time could not be converted to time format')
                    self.agent.send_kill_order()

            else:
                self.start_time_of_next_interval = now + real_time_increase - (now % real_time_increase)
                self.simulation_time = self.start_time_of_next_interval

        self.close_gates()
        self.async_future = asyncio.ensure_future(self.loop())

    def close_gates(self):
        if self.get_property('real_time_increase') > 0:
            self.agent.peri_gate.clear()
        if self.get_property('prep_lead') > 0:
            self.agent.prep_gate.clear()

    async def loop(self):
        while self.alive:

            time_increase = self.get_property('real_time_increase')
            prep_lead = self.get_property('prep_lead')

            if time_increase <= 0:
                time_increase = 0
                prep_lead = 0

            if prep_lead > 0:
                prep_sleep_amount = self.start_time_of_next_interval - prep_lead - time.time()
                if prep_sleep_amount < 0:
                    prep_sleep_amount = 0
                await asyncio.sleep(prep_sleep_amount)
                if not self.agent.prep_gate.is_set():
                    self.agent.prep_gate.set()

            sleep_amount = self.start_time_of_next_interval - time.time()
            await asyncio.sleep(sleep_amount)

            self.start_time_of_curr_interval = self.start_time_of_next_interval
            self.start_time_of_next_interval = self.start_time_of_next_interval + time_increase

            if not self.agent.prep_gate.is_set():
                self.agent.prep_gate.set()
            if not self.agent.peri_gate.is_set():
                self.agent.peri_gate.set()

    async def func_prep(self):

        self.set_output("step", self.model_run)
        is_live = self.get_property('mode') == 'live'
        self.set_output('is_live', is_live)

        simu_time_increase = self.get_property('simu_time_increase')
        interval = self.get_property("future_time_increase")
        steps = self.get_property("future_steps_amount")
        if steps < 1:
            steps = 1

        futures = [i * interval + self.simulation_time for i in range(steps)]
        self.set_output("times", futures)
        self.simulation_time += simu_time_increase

    async def func_in_sync(self):

        simu_number_of_intervals = self.get_property('simu_number_of_intervals')
        if simu_number_of_intervals > 0 and self.model_run + 1 >= simu_number_of_intervals:
            self.agent.end_all_model_loops()

        simu_stop_time_string = self.get_property('simu_stop_time')
        try:
            simu_stop_time = cal.timegm(time.strptime(simu_stop_time_string, '%Y-%m-%d %H:%M'))
        except ValueError:
            self.log_error(f'property simu_start_time could not be converted to time format')
            simu_stop_time = 0

        if simu_stop_time != 0 and simu_stop_time < self.simulation_time:
            self.agent.end_all_model_loops()

        self.close_gates()

    async def func_amend(self, keys=[]):
        if 'mode' in keys or 'simu_start_time' in keys:
            self.async_future.cancel()
            await self.func_birth()