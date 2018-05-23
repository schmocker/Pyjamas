import asyncio
from pyjama.core.supermodel import Supermodel

class Model(Supermodel):
    """
        schedules the func gates of the agent
        sets the number of elapsed rounds as output
    """

    def __init__(self, uuid, name: str):
        super(Model, self).__init__(uuid,name,["num_elapsed"])
        self.elapsed = 0
        self.properties["number_of_exec"] = -1
        self.properties["peri_interval"] = 0
        self.properties["prep_lead"] = 0
        self.properties["post_delay"] = 0

    def close_gates(self):
        if self.properties["prep_lead"] != 0:
            self.log_debug("closing prep gate")
            self.agent.prep_gate.clear()
        if self.properties["peri_interval"] != 0:
            self.log_debug("closing peri gate")
            self.agent.peri_gate.clear()
        if self.properties["post_delay"] != 0:
            self.log_debug("closing post gate")
            self.agent.post_gate.clear()

    async def loop(self):
        while (self.properties["number_of_exec"] > self.elapsed or self.properties["number_of_exec"] < 0) and self.alive:

            # TODO: change wait time to be relative to start time to remove cumulative error

            if self.properties["prep_lead"] != 0:
                self.log_debug("opening prep gate")
                self.agent.prep_gate.set()

            await asyncio.sleep(self.properties["prep_lead"])
            if self.properties["peri_interval"] != 0:
                self.log_debug("opening peri gate")
                self.agent.peri_gate.set()

            await asyncio.sleep(self.properties["post_delay"])
            if self.properties["post_delay"] != 0:
                self.log_debug("opening post gate")
                self.agent.post_gate.set()
            
            sleeptime = self.properties["peri_interval"] - self.properties["prep_lead"] - self.properties["post_delay"]
            await asyncio.sleep(sleeptime)
        
        self.log_debug("leaving scheduler loop")
    

    async def func_birth(self):
        if self.properties["number_of_exec"] == 0:
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
        if self.properties["number_of_exec"] <= self.elapsed and self.properties["number_of_exec"] >= 0:
            self.agent.end_all_model_loops()