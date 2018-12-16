import asyncio
from pyjamas_core.util import Input, Output, Property
from pyjamas_core.supermodel import Supermodel
import calendar as cal
import time

class Model(Supermodel):
    """
        schedules the func gates of the agent
        live mode
    """

    def __init__(self, uuid, name: str):
        super(Model, self).__init__(uuid, name)

        self.start_time_of_curr_interval = 0
        self.start_time_of_next_interval = 0
        self.async_future = None

        self.outputs['step'] = Output('Step', unit='-', info='step number, starts with 0')
        self.outputs['time'] = Output('Future', unit='s', info='utc time in seconds since epoch')

        # control
        self.properties['prep_lead'] = Property('Time lead of Preperation step', default=0, data_type=int, unit='s', info='Amount of seconds the preparation step is started before the actual interval')
        self.properties['delta_time'] = Property('Real time between each interval run', default=1, data_type=int, unit='s', info='Real time between iteration, 0 = as fast as possible')

    async def func_birth(self):
        # set simulation_time and start_time_of_next_interval

        now = time.time()

        time_increase = self.get_property('delta_time')

        if time_increase > 0:
            self.start_time_of_next_interval = now + time_increase - (now % time_increase)
        elif time_increase <= 0:
            self.start_time_of_next_interval = now

        self.close_gates()
        self.async_future = asyncio.ensure_future(self.loop())

    def close_gates(self):
        if self.get_property('delta_time') > 0:
            self.agent.peri_gate.clear()
        if self.get_property('prep_lead') > 0:
            self.agent.prep_gate.clear()

    async def loop(self):

        while self.alive:

            time_increase = self.get_property('delta_time')
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

                time_increase = self.get_property('delta_time')
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
        self.set_output("time", self.start_time_of_curr_interval)

    async def func_in_sync(self):
        self.close_gates()
