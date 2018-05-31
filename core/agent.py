import asyncio
from multiprocessing import Process
import logging
import concurrent

class Agent(Process):

    def __init__(self, agent_id, name: str, controller_queue, agent_queue, DEBUG):
        super(Agent,self).__init__()

        self.agent_queue = agent_queue
        self.controller_queue = controller_queue

        self.id = agent_id
        self.name = name
        self.models = {}

        self.running = False
        self.paused = False

        self.logger = None
        self.DEBUG = DEBUG

    def log_debug(self, msg):
        if self.logger:
            self.logger.debug(f"[AGENT][{__name__}][{self.name}] : {msg}")

    def log_warning(self, msg):
        if self.logger:
            self.logger.warning(f"[AGENT][{__name__}][{self.name}] : {msg}")

    def run(self):

        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        self.running = True

        self.logger = logging.getLogger(__name__)
        if self.DEBUG:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.WARNING)
        con = logging.FileHandler("pyjama_log_" + str(self.id) + "_" + str(self.name) + ".txt")
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

        # pause gate
        self.pause_gate = asyncio.Event()

        # func gates
        self.prep_gate = asyncio.Event()
        self.peri_gate = asyncio.Event()
        self.post_gate = asyncio.Event()

        # open func gates
        self.prep_gate.set()
        self.peri_gate.set()
        self.post_gate.set()

        # open pause gate
        self.pause_gate.set()

        # event loop
        self.loop = asyncio.get_event_loop()

        self.log_debug("starting simulation")
        self.start_simulation()
        self.log_debug("finished simulation")

        self.send_dead_order()
        self.log_debug("sent dead order")

    def prepare_models(self):
        # execute func_birth for all models
        self.log_debug("started preparing models")
        births = [asyncio.ensure_future(model._internal_birth()) for i,model in self.models.items()]
        try:
            self.loop.run_until_complete(asyncio.gather(*births))
            self.log_debug("finished preparing models")
            return True
        except Exception:
            self.log_warning(f'failed to execute all func_births --> stopping simulation')
            return False

    def start_simulation(self):
        # func_birth is executed and finished for all models before anything else
        if not self.prepare_models():
            return

        # start the internal loop of all models
        self.log_debug("starting internal loop of all models")
        preps = [asyncio.ensure_future(model.internal_loop()) for i,model in self.models.items()]
        preps.append(asyncio.ensure_future(self.read_queue()))
        try:
            # main loop
            self.loop.run_until_complete(asyncio.gather(*preps))
        except concurrent.futures._base.CancelledError:
            self.log_debug(f'all tasks killed')

        self.running = False

    def add_model(self, model_to_add):
        try:
            self.models[model_to_add.id] = model_to_add
            model_to_add.agent = self
            return True
        except KeyError:
            return False

    def remove_model(self, model_id):
        try:
            rem_mod = self.models[model_id]
            for i, model in self.models.items():
                for inp, out in model.inputs.items():
                    if out[1] == rem_mod:
                        del model.inputs[inp]
            del self.models[rem_mod.id]
            return True
        except KeyError:
            return False


    def link_models(self, output_model_id, output_name, input_model_id, input_name):
        try:
            input_model = self.models[input_model_id]
            output_model = self.models[output_model_id]

            input_model.link_input(output_model,output_name,input_name)
            return True
        except KeyError:
            return False

    def unlink_models(self, output_model_id, output_name, input_model_id, input_name):
        try:
            input_model = self.models[input_model_id]
            linked_output_model, linked_output_name = input_model[input_name]

            if linked_output_model.id == output_model_id and linked_output_name == output_name:
                input_model.unlink_input(input_name)
                return True
            else:
                return False
        except KeyError:
            return False


    def set_property(self, model_id, property_name, property_value):
        try:
            self.models[model_id].set_property(property_name,property_value)
            return True
        except KeyError:
            return False

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
            await self.pause_gate.wait()
            self.sync_gate_first.clear()
            self.sync_gate_second.set()
            self.sync_counter_second = 0
            self.log_debug("second sync gate opened")


    # reading queue and handling messages
        
    async def read_queue(self):
        while self.running:
            if not self.agent_queue.empty():
                try:
                    msg = self.agent_queue.get(False)
                    if self.id == msg["agent"]:
                        await self.handle_order(msg) 
                except KeyError:
                    self.log_debug("non valid message format")
                except Exception:
                    self.log_debug("queue was empty")
            await asyncio.sleep(0)

    async def handle_order(self, msg):
        try:
            order = msg['order']
            self.log_debug(f'recieved order "{order}"')

            if order == "halt":
                self.pause()
            elif order == "cont":
                self.unpause()
            elif order == "stop":
                self.end_all_model_loops()
            elif order == "prop":
                # send prep change to model
                model_id = msg["model"]
                property_name = msg["text"]["property_name"]
                property_value = msg["text"]["property_value"]
                self.models[model_id].set_property(property_name, property_value)
            elif order == "data":
                # TODO: implement
                # return data
                pass
            else:
                self.log_debug(f'recieved order could not be executed')
        except KeyError:
            self.log_warning(f'message could not be handled correctly')
            self.log_warning(f'message = {msg}')

    def pause(self):
        self.pause_gate.clear()
        self.log_debug(f'pause gate closed')
        self.paused = True

    def unpause(self):
        self.pause_gate.set()
        self.log_debug(f'pause gate opened')
        self.paused = False

    def end_all_model_loops(self):
        for i, model in self.models.items():
            model.alive = False
        self.log_debug("set all model.alive to False")
        if self.paused:
            self.unpause()
        self.running = False

    # sending messages

    def send_dead_order(self):
        order = {}
        order["order"] = "dead"
        order["agent"] = self.id
        self.controller_queue.put(order)