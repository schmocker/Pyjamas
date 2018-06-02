import asyncio
from core.util import Input, Output, Property
from core.supermodel import Supermodel

class Model(Supermodel):
    """
        schedules the func gates of the agent
        sets the number of elapsed rounds as output
    """

    def __init__(self, uuid, name: str):
        super(Model, self).__init__(uuid,name)
        self.elapsed = 0

        self.outputs['num_elapsed'] = Output({'name': 'Number Elapsed', 'unit': 'int', 'dimensions': []})

        self.properties["number_of_exec"] = Property(-1, {'name': 'Number of Executions', 'unit': 'int', 'dimensions': []})
        self.properties["peri_interval"] = Property(0, {'name': 'Peri Interval', 'unit': 'num', 'dimensions': []})
        self.properties["prep_lead"] = Property(0, {'name': 'Prep lead', 'unit': 'num', 'dimensions': []})
        self.properties["post_delay"] = Property(0, {'name': 'Post delay', 'unit': 'num', 'dimensions': []})

    def close_gates(self):
        if self.get_property('prep_lead') != 0:
            self.log_debug("closing prep gate")
            self.agent.prep_gate.clear()
        if self.get_property('peri_interval') != 0:
            self.log_debug("closing peri gate")
            self.agent.peri_gate.clear()
        if self.get_property('post_delay') != 0:
            self.log_debug("closing post gate")
            self.agent.post_gate.clear()

    async def loop(self):
        while (self.get_property('number_of_exec') > self.elapsed or self.get_property('number_of_exec') < 0) and self.alive:

            # TODO: change wait time to be relative to start time to remove cumulative error

            if self.get_property('prep_lead') != 0:
                self.log_debug("opening prep gate")
                self.agent.prep_gate.set()

            await asyncio.sleep(self.get_property('prep_lead'))
            if self.get_property('peri_interval') != 0:
                self.log_debug("opening peri gate")
                self.agent.peri_gate.set()

            await asyncio.sleep(self.get_property('post_delay'))
            if self.get_property('post_delay') != 0:
                self.log_debug("opening post gate")
                self.agent.post_gate.set()
            
            sleeptime = self.get_property('peri_interval') - self.get_property('prep_lead') - self.get_property('post_delay')
            await asyncio.sleep(sleeptime)
        
        self.log_debug("leaving scheduler loop")
    

    async def func_birth(self):
        if self.get_property('number_of_exec') == 0:
            self.agent.end_all_model_loops()
            return

        self.close_gates()
        asyncio.ensure_future(self.loop())

    async def func_prep(self):
        self.set_output("num_elapsed", self.elapsed)

    async def func_post(self, peri_to_post=None):
        self.elapsed = self.elapsed + 1

    async def func_in_sync(self):
        self.close_gates()
        if self.get_property('number_of_exec') <= self.elapsed and self.get_property('number_of_exec') >= 0:
            self.agent.end_all_model_loops()