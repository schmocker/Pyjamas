import asyncio
from multiprocessing import Process
import logging
import concurrent
import datetime
from core.util import CreateDirFileHandler
import traceback

class Agent():
    """Handles all models in a simulation and the communication with the controller
    
    Arguments:
        agent_id {'Any'} -- the id of the agent
        name {str} -- the name of the agent
        controller_queue {'multiprocessing.Queue'} -- the controller queue
        agent_queue {'multiprocessing.Queue'} -- the agent queue
    
    Keyword Arguments:
        logging_path {str} -- the path for the logger, if None no logging will take place (default: {None})
        DEBUG {bool} -- if True, will log on debug level (default: {False})
    """

    def __init__(self, agent_id: 'Any', name: str, controller_queue, agent_queue, logging_path: str=None, DEBUG: bool=False):
        super(Agent,self).__init__()

        # controller to agent queue
        self.agent_queue = agent_queue
        # agent to controller queue
        self.controller_queue = controller_queue

        self.id = agent_id
        self.name = name
        self.models = {}

        self.running = False
        self.paused = False

        self.logger = None
        self.logging_path = logging_path
        self.DEBUG = DEBUG

#region logging

    def create_logger(self, logging_path: str, DEBUG: bool):
        if logging_path:
            self.logger = logging.getLogger(__name__)
            
            if self.DEBUG:
                self.logger.setLevel(logging.DEBUG)
            else:
                self.logger.setLevel(logging.INFO)
            try:
                con = CreateDirFileHandler(f"{logging_path}/pyjama_log_{self.id}_{self.name}_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt")
                con.setLevel(logging.DEBUG)
                formatter = logging.Formatter('[%(asctime)s][%(levelname)s][%(name)s][%(processName)s] : %(message)s')
                con.setFormatter(formatter)
                self.logger.addHandler(con)
                self.log_debug("initialized logger")
            except Exception as e:
                print("Failed to create logger")
                print(e)
        else:
            self.logger = None

    def log_debug(self, msg: str):
        if self.logger:
            self.logger.debug(f"[AGENT][{__name__}][{self.name}] : {msg}")

    def log_warning(self, msg: str):
        print(f"[WARNING][AGENT][{__name__}][{self.name}] : {msg}")
        print(traceback.format_exc())
        if self.logger:
            self.logger.warning(f"[AGENT][{__name__}][{self.name}] : {msg}")
            self.logger.warning(f"[AGENT][{__name__}][{self.name}] : {traceback.format_exc()}")

    def log_error(self, msg: str):
        print(f"[ERROR][AGENT][{__name__}][{self.name}] : {msg}")
        print(traceback.format_exc())
        if self.logger:
            self.logger.error(f"[AGENT][{__name__}][{self.name}] : {msg}")
            self.logger.error(f"[AGENT][{__name__}][{self.name}] : {traceback.format_exc()}")

#endregion logging

#region simulation

    def run(self):
        """setup and start simulation
        """

        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        self.running = True

        self.create_logger(self.logging_path, self.DEBUG)

        # sync gates
        self.sync_gate_first = asyncio.Event()
        self.sync_gate_second = asyncio.Event()

        self.sync_counter_first = 0
        self.sync_counter_second = 0

        # pause gate
        self.pause_gate = asyncio.Event()

        # open pause gate
        self.pause_gate.set()

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

        self.running = False
        self.send_dead_order()
        self.log_debug("sent dead order")

    def prepare_models(self) -> bool:
        """executes func_birth for all models
        
        Returns:
            bool -- False if an exception was thrown, True otherwise
        """

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
        """start a new simulation run
        """

        # func_birth is executed and finished for all models before anything else
        if not self.prepare_models():
            return

        # start the simulation loop of all models
        self.log_debug("starting simulation loop of all models")
        preps = [asyncio.ensure_future(model.simulation_loop()) for i,model in self.models.items()]
        preps.append(asyncio.ensure_future(self.read_queue()))
        try:
            # main loop
            self.loop.run_until_complete(asyncio.gather(*preps))
        except concurrent.futures._base.CancelledError:
            self.log_debug(f'all tasks killed')
        except Exception:
            self.log_error(f'an exeption was thrown during the simulation --> stopping simulation')
            self.send_kill_order()

        self.running = False

    async def syncFirst(self):
        """first sync gate ensures that all models have finished post
        first sync gate gets opened when all models have called syncFirst()
        """

        self.sync_counter_first = self.sync_counter_first + 1
        self.log_debug(f"first sync gate counter: {self.sync_counter_first}/{len(self.models)}")
        if self.sync_counter_first >= len(self.models):
            self.sync_gate_second.clear()
            self.sync_gate_first.set()
            self.sync_counter_first = 0
            self.log_debug("first sync gate opened")

    async def syncSecond(self):
        """second sync gate ensures that all models have finished func_in_sync and cleared their outputs
        second sync gate gets opened when all models have called syncSecond()
        if the agent is paused it will wait before opening the second sync gate
        """

        self.sync_counter_second = self.sync_counter_second + 1
        self.log_debug(f"second sync gate counter: {self.sync_counter_second}/{len(self.models)}")
        if self.sync_counter_second >= len(self.models):
            await self.pause_gate.wait()
            # after pause read agent queue until empty to ensure that all pending changes are applied
            await self.force_read_queue()
            self.sync_gate_first.clear()
            self.sync_gate_second.set()
            self.sync_counter_second = 0
            self.log_debug("second sync gate opened")

#endregion simulation

#region controlling

    def add_model(self, model_to_add: 'Supermodel') -> bool:
        """add a model to the agent
        
        Arguments:
            model_to_add {'Supermodel'} -- the model to add
        
        Returns:
            bool -- True if model could be added, False otherwise
        """

        try:
            self.models[model_to_add.id] = model_to_add
            model_to_add.agent = self
            return True
        except KeyError:
            return False

    def remove_model(self, model_id: 'Any') -> bool:
        """remove a model by its id
        
        Arguments:
            model_id {'Any'} -- the id of the model to be removed
        
        Returns:
            bool -- True if the model could be removed, False otherwise
        """

        try:
            rem_mod = self.models[model_id]
            # remove all links pointing to this model
            for _, model in self.models.items():
                for inp, out in model.inputs.items():
                    if out[1] == rem_mod:
                        del model.inputs[inp]
            del self.models[rem_mod.id]
            return True
        except KeyError:
            return False

    def link_models(self, output_model_id: 'Any', output_name: str, input_model_id: 'Any', input_name: str) -> bool:
        """links the output of one model to the input of another
        
        Arguments:
            output_model_id {'Any'} -- the id of the model providing the output
            output_name {str} -- the name of the output port
            input_model_id {'Any'} -- the id of the model providing the input
            input_name {str} -- the name of the input port
        
        Returns:
            bool -- True if the link could be created, False otherwise
        """

        try:
            input_model = self.models[input_model_id]
            output_model = self.models[output_model_id]

            return input_model.link_input(output_model,output_name,input_name)
        except KeyError:
            return False

    def unlink_models(self, output_model_id: 'Any', output_name: str, input_model_id: 'Any', input_name: str) -> bool:
        """remove an existing link
        
        Arguments:
            output_model_id {'Any'} -- the id of the model providing the output
            output_name {str} -- the name of the output port
            input_model_id {'Any'} -- the id of the model providing the input
            input_name {str} -- the name of the input port
        
        Returns:
            bool -- True if the link could be removed, False otherwise
        """

        try:
            input_model = self.models[input_model_id]
            linked_output_model, linked_output_name = input_model[input_name]

            if linked_output_model.id == output_model_id and linked_output_name == output_name:
                return input_model.unlink_input(input_name)
            else:
                return False
        except KeyError:
            return False

    def set_property(self, model_id: 'Any', property_name: str, property_value: 'Any') -> bool:
        """set a new value for a model property
        
        Arguments:
            model_id {'Any'} -- the id of the model
            property_name {str} -- the name of the property port
            property_value {'Any'} -- the new value of the property
        
        Returns:
            bool -- True if the property could be changed, False otherwise
        """
        
        try:
            if self.running:
                self.models[model_id].set_amend_property(property_name,property_value)
            else:
                self.models[model_id].set_property(property_name,property_value)
            return True
        except KeyError:
            return False

    def get_info(self) -> dict:
        """returns a dictionary with all port infos of every model
        
        Returns:
            dict -- the dictionary containing the info
        """

        info = {}
        info['id'] = self.id
        info['name'] = self.name
        info['models'] = {}
        for _, mod in self.models.items():
            info['models'][mod.id] = mod.get_info()
        return info

#endregion controlling

#region messaging

    # reading queue and handling messages
        
    async def read_queue(self):
        """reads the agent queue while the agent is running
        """

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

    async def force_read_queue(self):
        """reads the agent queue until empty
        """

        while not self.agent_queue.empty():
            try:
                msg = self.agent_queue.get(False)
                if self.id == msg["agent"]:
                    await self.handle_order(msg) 
            except KeyError:
                self.log_debug("non valid message format")
            except Exception:
                self.log_debug("queue was empty")

    async def handle_order(self, msg: dict):
        """accepts new order and calls the coresponding function
        
        Arguments:
            msg {dict} -- the dictionary containing the order
        """

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
                self.set_property(model_id, property_name, property_value)
            else:
                self.log_debug(f'recieved order could not be executed')
        except KeyError:
            self.log_warning(f'message does not have the right format')

    def pause(self):
        self.pause_gate.clear()
        self.log_debug(f'pause gate closed')
        self.paused = True

    def unpause(self):
        self.pause_gate.set()
        self.log_debug(f'pause gate opened')
        self.paused = False

    def end_all_model_loops(self):
        """stop the run by setting 'alive' to False for all models
        The models will exit the simulation after finishing the current run
        """

        for _, model in self.models.items():
            model.alive = False
        self.log_debug("set all model.alive to False")
        if self.paused:
            self.unpause()
        self.running = False

    # sending messages

    def send_dead_order(self):
        order = {}
        order['order'] = 'dead'
        order['agent'] = self.id
        self.controller_queue.put(order)

    def send_kill_order(self):
        order = {}
        order['order'] = 'kill'
        order['agent'] = self.id
        self.controller_queue.put(order)

    def send_data_order(self, model_id: 'Any', data: list):
        order = {}
        order['order'] = 'data'
        order['agent'] = self.id
        order['model'] = model_id
        order['text'] = data
        self.controller_queue.put(order)

    def send_cpro_order(self, model_id: 'Any', props: dict):
        order = {}
        order['order'] = 'cpro'
        order['agent'] = self.id
        order['model'] = model_id
        order['text'] = props
        self.controller_queue.put(order)

#endregion messaging