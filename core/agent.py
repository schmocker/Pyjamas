import asyncio
from multiprocessing import Process
from Lib import queue
import logging

class Agent(Process):

    def __init__(self, name: str, queue):
        super(Agent,self).__init__()

        self.queue = queue

        self.name = name
        self.models = {}

        self.running = False

        self.logger = logging.getLogger(__name__)

    def log_debug(self, msg):
        self.logger.debug(f"[AGENT][{__name__}][{self.name}] : {msg}")

    def run(self):

        self.running = True

        self.logger.setLevel(logging.DEBUG)
        con = logging.FileHandler("pyjama_log_" + self.name + ".txt")
        con.setLevel(logging.DEBUG)
        formatter = logging.Formatter('[%(asctime)s][%(levelname)s][%(name)s][%(processName)s] : %(message)s')
        con.setFormatter(formatter)
        self.logger.addHandler(con)
        self.log_debug("initialized logger")

        self.sync_counter_first = 0
        self.sync_counter_second = 0

        # sync gates
        self.sync_gate_first = asyncio.Event()
        self.sync_gate_second = asyncio.Event()

        # func gates
        self.prep_gate = asyncio.Event()
        self.peri_gate = asyncio.Event()
        self.post_gate = asyncio.Event()

        # open func gates
        self.prep_gate.set()
        self.peri_gate.set()
        self.post_gate.set()

        # event loop
        self.loop = asyncio.get_event_loop()

        self.log_debug("starting simulation")
        self.start_simulation()
        self.log_debug("finished simulation")

        self.log_debug("sending dead order")
        self.send_dead_order(self.name)

    def prepare_models(self):
        # execute func_birth for all models
        self.log_debug("started preparing models")
        births = [asyncio.ensure_future(model._internal_birth()) for i,model in self.models.items()]
        self.loop.run_until_complete(asyncio.gather(*births))
        self.log_debug("finished preparing models")

    def start_simulation(self):
        # func_birth is executed and finished for all models before anything else
        self.prepare_models()

        # start the internal loop of all models
        self.log_debug("starting internal loop of all models")
        preps = [asyncio.ensure_future(model.internal_loop()) for i,model in self.models.items()]
        preps.append(asyncio.ensure_future(self.read_queue()))
        self.loop.run_until_complete(asyncio.gather(*preps))

        self.running = False

    def add_model(self, model_to_add):
        self.models[model_to_add.id] = model_to_add
        model_to_add.agent = self
        self.log_debug(f"model {model_to_add.name} added")
        return model_to_add.id

    def remove_model(self, model_id):
        rem_mod = self.models[model_id]
        for i, model in self.models.items():
            for inp, out in model.inputs.items():
                if out[1] == rem_mod:
                    del model.inputs[inp]
        del self.models[rem_mod.id]
        self.log_debug(f"model {rem_mod.name} removed")


    def link_models(self, output_model_id, output_name, input_model_id, input_name):
        input_model = self.models[input_model_id]
        output_model = self.models[output_model_id]

        input_model.link_input(output_model,output_name,input_name)
        self.log_debug(f"linked {output_model.name}:{output_name} to {input_model.name}:{input_name}")

    def set_property(self, model_id, property_name, property_value):

        self.models[model_id].set_property(property_name,property_value)

    async def syncFirst(self):
        # first sync gate ensures that all models have finished post
        self.sync_counter_first = self.sync_counter_first + 1
        self.log_debug(f"first sync gate counter: {self.sync_counter_first}/{len(self.models)}")
        if self.sync_counter_first >= len(self.models):
            self.sync_gate_second.clear()
            self.sync_gate_first.set()
            self.sync_counter_first = 0
            self.log_debug("first sync gate opened")

    async def syncSecond(self):
        # second sync gate ensures that all models have finished func_in_sync and cleared their outputs
        self.sync_counter_second = self.sync_counter_second + 1
        self.log_debug(f"second sync gate counter: {self.sync_counter_second}/{len(self.models)}")
        if self.sync_counter_second >= len(self.models):
            self.sync_gate_first.clear()
            self.sync_gate_second.set()
            self.sync_counter_second = 0
            self.log_debug("second sync gate opened")

    def end_all_model_loops(self):
        for i, model in self.models.items():
            model.alive = False
        self.log_debug("set all model.alive to False")
        self.running = False

    def kill_all_model_loops(self):
        for task in asyncio.Task.all_tasks(self.loop):
            task.cancel()
        self.log_debug("canceled all tasks")
        self.running = False
        
    async def read_queue(self):
        while self.running:
            if not self.queue.empty():
                try:
                    msg = self.queue.get(False)
                    if self.name == msg["agent"]:
                        await self.handle_input(msg) 
                    else:
                        self.queue.put(msg)
                except Exception:
                    self.log_debug("queue was empty")
            await asyncio.sleep(.1)

    async def handle_input(self, msg):
        order = msg['order']
        self.log_debug(f'recieved order "{order}"')

        if order == "stop":
            self.end_all_model_loops()
        elif order == "prop":
            # send prep change to model
            model_id = msg["model"]
            property_name = msg["text"]["property_name"]
            property_value = msg["text"]["property_value"]
            self.models[model_id].set_property(property_name, property_value)
        elif order == "kill":
            # kill all tasks
            self.kill_all_model_loops()
        elif order == "data":
            # TODO: implement
            # return data
            pass
        else:
            self.log_debug(f'recieved order could not be executed')

    def send_dead_order(self, agent_name):
        order = {}
        order["order"] = "dead"
        order["agent"] = agent_name
        self.queue.put(order)