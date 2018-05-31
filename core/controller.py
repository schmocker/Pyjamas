import importlib
import uuid
import multiprocessing
import json
import time
from threading import Thread
import logging

class Controller():

    def __init__(self):
        self.agents = {}
        self.agents_running = []
        self.agents_paused = []
        self.controller_queue = multiprocessing.Queue()
        self.agent_queues = {}
        self.thread_running = False


        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        con = logging.FileHandler("pyjama_log_Controller.txt")
        con.setLevel(logging.DEBUG)
        formatter = logging.Formatter('[%(asctime)s][%(levelname)s][%(name)s][%(processName)s] : %(message)s')
        con.setFormatter(formatter)
        self.logger.addHandler(con)
        self.log_debug("initialized logger")

    def log_debug(self, msg):
        if self.logger:
            self.logger.debug(f"[CONTROLLER][{__name__}] : {msg}")

    def log_error(self, msg):
        if self.logger:
            self.logger.error(f"[CONTROLLER][{__name__}] : {msg}")

    def add_agent(self, agent_id, agent_name: str):
        self.log_debug('starting add_agent')
        try:
            if self.is_existing_agent(agent_id):
                self.log_error(f'agent with id {agent_id} is already existing')
                return False
            agent_queue = multiprocessing.Queue()
            self.agent_queues[agent_id] = agent_queue
            a = importlib.import_module("core.agent").Agent(agent_id, agent_name, self.controller_queue, agent_queue)
            self.log_debug(f'created agent (agent_id = {a.id} agent_name = {a.name})')
            self.agents[agent_id] = a
            self.log_debug(f'added agent (agent_id = {a.id} agent_name = {a.name})')
            if not self.thread_running:
                self.start()
                self.log_debug(f'started queue reading thread')
            return True
        except Exception:
            self.log_debug(f'agent {agent_id} could not be added')
        return False

    def remove_agent(self, agent_id: str):
        self.log_debug('starting remove_agent')
        try:
            if self.is_agent_running(agent_id):
                self.log_debug(f'agent {agent_id} is running')
                self.kill_agent(agent_id)
            del self.agent_queues[agent_id]
            del self.agents[agent_id]
            if self.is_agent_paused(agent_id):
                self.agents_paused.remove(agent_id)
            self.log_debug(f'agent {agent_id} removed')
            if len(self.agents) <= 0:
                self.stop()
                self.log_debug(f'stopped queue reading thread')
            return True
        except Exception:
            self.log_debug(f'agent {agent_id} could not be removed')
        return False
    
    def add_model(self, agent_id, model_path: str, model_id, model_name: str):
        self.log_debug('starting add_model')
        if self.is_existing_agent(agent_id):
            if not self.is_agent_running(agent_id):
                mod = importlib.import_module(f"Models.{model_path}").Model(model_id,model_name)
                self.log_debug(f'created model (model_id = {model_id} model_name = {model_name})')
                if self.agents[agent_id].add_model(mod):
                    self.log_debug(f'added model (model_id = {model_id} model_name = {model_name}) to agent {agent_id}')
                    return True
                else:
                    self.log_error(f'model (model_id = {model_id} model_name = {model_name}) could not be added')
            else:
                self.log_debug(f'agent {agent_id} is running -> model was not added')
        return False

    def remove_model(self, agent_id, model_id):
        self.log_debug('starting remove_model')
        if self.is_existing_agent(agent_id):
            if not self.is_agent_running(agent_id):
                if self.agents[agent_id].remove_model(model_id):
                    self.log_debug(f'removed model {model_id} from agent {agent_id}')
                    return True
                else:
                    self.log_error(f'model {model_id} could not be removed')
            else:
                self.log_debug(f'agent {agent_id} is running -> model was not removed')
        return False
    
    def link_models(self, agent_id, output_model_id, output_name: str, input_model_id, input_name: str):
        self.log_debug('starting link_models')
        if self.is_existing_agent(agent_id):
            if not self.is_agent_running(agent_id):
                if self.agents[agent_id].link_models(output_model_id,output_name,input_model_id,input_name):
                    self.log_debug(f'added link from (model {output_model_id} / output {output_name}) to (model {input_model_id} / input {input_name}) in agent {agent_id}')
                    return True
                else:
                    self.log_error(f'link from (model {output_model_id} / output {output_name}) to (model {input_model_id} / input {input_name}) in agent {agent_id} could not be created')
            else:
                self.log_debug(f'agent {agent_id} is running -> models were not linked')
        return False

    def unlink_models(self, agent_id, output_model_id, output_name: str, input_model_id, input_name: str):
        self.log_debug('starting unlink_models')
        if self.is_existing_agent(agent_id):
            if not self.is_agent_running(agent_id):
                if self.agents[agent_id].unlink_models(output_model_id,output_name,input_model_id,input_name):
                    self.log_debug(f'removed link from (model {output_model_id}:{output_name}) to (model {input_model_id}:{input_name}) in agent {agent_id}')
                    return True
                else:
                    self.log_error(f'link from (model {output_model_id}:{output_name}) to (model {input_model_id}:{input_name}) in agent {agent_id} could not be removed')
            else:
                self.log_debug(f'agent {agent_id} is running -> models were not unlinked')
        return False

    def set_property(self, agent_id, model_id, property_name: str, property_value):
        self.log_debug('starting set_property')
        if self.is_existing_agent(agent_id):
            if self.is_agent_running(agent_id):
                if self.send_set_property_order(agent_id,model_id,property_name,property_value):
                    self.log_debug(f'set property {property_name} of model {model_id} in agent {agent_id}')
                    return True
            else:
                if self.agents[agent_id].set_property(model_id,property_name,property_value):
                    self.log_debug(f'set property {property_name} of model {model_id} in agent {agent_id}')
                    return True
                else:
                    self.log_error(f'property {property_name} of model {model_id} in agent {agent_id} could not be set')
        return False

    def start_agent(self, agent_id):
        self.log_debug('starting start_agent')
        if self.is_existing_agent(agent_id):
            if self.is_agent_paused(agent_id):
                self.log_debug(f'agent {agent_id} already running but paused')
                if self.unpause_agent(agent_id):
                    self.log_debug(f'agent {agent_id} unpaused')
                    return True
            elif not self.is_agent_running(agent_id):
                self.agents_running.append(agent_id)
                self.agents[agent_id].start()
                self.log_debug(f'agent {agent_id} started')
                return True
        return False

    def pause_agent(self, agent_id):
        self.log_debug(f'starting pause_agent')
        if self.is_existing_agent(agent_id):
            if self.is_agent_paused(agent_id):
                self.log_debug(f'agent {agent_id} is already paused')
                return True
            if self.is_agent_running(agent_id):
                if self.send_halt_order(agent_id):
                    self.agents_paused.append(agent_id)
                    return True
        return False

    def unpause_agent(self, agent_id):
        self.log_debug('starting unpause_agent')
        if self.is_existing_agent(agent_id):
            if self.is_agent_running(agent_id):
                if self.is_agent_paused(agent_id):
                    if self.send_cont_order(agent_id):
                        self.agents_paused.remove(agent_id)
                        return True
                else:
                    self.log_debug(f'agent {agent_id} is not paused')
                    return True
            else:
                self.log_debug(f'agent {agent_id} is not running')
                return True
        return False

    def stop_agent(self, agent_id):
        self.log_debug(f'starting stop_agent')
        if self.is_existing_agent(agent_id):
            if self.is_agent_running(agent_id):
                if self.send_stop_order(agent_id):
                    return True
        return False

    def kill_agent(self, agent_id):
        self.log_debug(f'starting kill_agent')
        if self.is_existing_agent(agent_id):
            if self.is_agent_running(agent_id):
                self.agents[agent_id].terminate()
                if self.is_agent_paused(agent_id):
                    self.agents_paused.remove(agent_id)
                self.agents_running.remove(agent_id)
                return True
            else:
                self.log_debug(f'agent {agent_id} is not running')
                return True
        return False

    def is_existing_agent(self, agent_id):
        if agent_id in self.agents:
            return True
        self.log_error(f'agent {agent_id} is not existing')
        return False

    def is_agent_running(self, agent_id):
        if agent_id in self.agents_running:
            return True
        return False

    def is_agent_paused(self, agent_id):
        if self.is_agent_running(agent_id):
            if agent_id in self.agents_paused:
                return True
        return False

    def get_agents_running(self):
        return list(self.agents_running)

    def get_agents(self):
        return list(self.agents.keys())

    # queue reader

    def start(self):
        self.thread_running = True
        thread = Thread(target=self.read_queue)
        thread.daemon = True
        thread.start()

    def stop(self):
        self.thread_running = False

    def read_queue(self):
        self.log_debug(f'starting controller queue thread')
        while self.thread_running or self.agents_running:
            try:
                msg = self.controller_queue.get(True)
                self.handle_order(msg)
            except Exception as e:
                print(e)
        self.log_debug(f'finished controller queue thread')

    def handle_order(self, msg):
        try:
            self.log_debug(f'recieved order {msg["order"]} from agent {msg["agent"]}')
            if msg["order"] == "dead":
                agent_id = msg['agent']
                if self.is_agent_running(agent_id):
                    self.agents_running.remove(agent_id)
                if self.is_agent_paused(agent_id):
                    self.agents_paused.remove(agent_id)
                self.log_debug(f'agent {agent_id} removed from running list')
        except KeyError:
            self.log_error(f'message could not be handled correctly')
            self.log_error(f'message = {msg}')

    # orders

    def send_set_property_order(self, agent_id, model_id, property_name, property_value):
        text = {}
        text["property_name"] = property_name
        text["property_value"] = property_value

        order = {}
        order["order"] = "prop"
        order["agent"] = agent_id
        order["model"] = model_id
        order["text"] = text

        return self.send_order(agent_id, order)

    def send_stop_order(self, agent_id):
        order = {}
        order["order"] = "stop"
        order["agent"] = agent_id

        return self.send_order(agent_id, order)

    def send_halt_order(self, agent_id):
        order = {}
        order["order"] = "halt"
        order["agent"] = agent_id
        
        return self.send_order(agent_id, order)

    def send_cont_order(self, agent_id):
        order = {}
        order["order"] = "cont"
        order["agent"] = agent_id
        
        return self.send_order(agent_id, order)

    def send_order(self, agent_id, order):
        try:
            self.agent_queues[agent_id].put(order)
            self.log_debug(f'sent order {order["order"]} to agent {order["agent"]}')
            return True
        except KeyError:
            self.log_error(f'no queue found for agent_id {agent_id}')
        return False