import importlib
import uuid
import multiprocessing
import json
import time
from threading import Thread
import logging
import datetime
from core.util import CreateDirFileHandler

class Controller():

    def __init__(self, logging_path=None, DEBUG=False):
        self.agents = {}
        self.agents_running = {}
        self.agents_paused = []
        self.controller_queue = multiprocessing.Queue()
        self.agent_queues = {}
        self.thread_running = False

        self.logging_path = logging_path
        self.DEBUG = DEBUG

        self.result_data = {}
        self.property_data = {}
        self.model_runs = {}

        self.create_logger(logging_path, DEBUG)

#region logging

    def create_logger(self, logging_path, DEBUG):
        if logging_path:
            self.logger = logging.getLogger(__name__)
            if self.DEBUG:
                self.logger.setLevel(logging.DEBUG)
            else:
                self.logger.setLevel(logging.INFO)
            try:
                con = CreateDirFileHandler(f"{logging_path}/pyjama_log_Controller_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt")
                con.setLevel(logging.DEBUG)
                formatter = logging.Formatter('[%(asctime)s][%(levelname)s][%(name)s][%(processName)s] : %(message)s')
                con.setFormatter(formatter)
                self.logger.addHandler(con)
                self.log_debug("initialized logger")
            except Exception as e:
                print("Failed to create file logger")
                print(e)
        else:
            self.logger = None

    def log_debug(self, msg):
        if self.logger:
            self.logger.debug(f"[CONTROLLER][{__name__}] : {msg}")

    def log_warning(self, msg):
        if self.logger:
            self.logger.warning(f"[CONTROLLER][{__name__}] : {msg}")

#endregion logging

#region agent

    def add_agent(self, agent_id, agent_name: str):
        self.log_debug('starting add_agent')
        try:
            if agent_id in self.agents:
                self.log_warning(f'agent with id {agent_id} is already existing')
                return False
            agent_queue = multiprocessing.Queue()
            self.agent_queues[agent_id] = agent_queue
            a = importlib.import_module("core.agent").Agent(agent_id, agent_name, self.controller_queue, agent_queue, self.logging_path, self.DEBUG)
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

    def force_add_agent(self, agent_id, agent_name):
        self.log_debug('starting force_add_agent')
        if self.is_existing_agent(agent_id):
            if not self.remove_agent(agent_id):
                return False
        return self.add_agent(agent_id, agent_name)

    def remove_agent(self, agent_id):
        self.log_debug('starting remove_agent')
        try:
            if self.is_agent_running(agent_id):
                self.log_debug(f'agent {agent_id} is running')
                self.kill_agent(agent_id)
            del self.agent_queues[agent_id]
            del self.agents[agent_id]
            del self.result_data[agent_id]
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

    def get_agent_info(self, agent_id):
        if self.is_existing_agent(agent_id):
            return self.agents[agent_id].get_info()
        return None
    
#endregion agent

#region model

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
                    self.log_warning(f'model (model_id = {model_id} model_name = {model_name}) could not be added')
            else:
                self.log_debug(f'agent {agent_id} is running -> model was not added')
        return False

    def remove_model(self, agent_id, model_id):
        self.log_debug('starting remove_model')
        if self.is_existing_agent(agent_id):
            if not self.is_agent_running(agent_id):
                if self.agents[agent_id].remove_model(model_id):
                    del self.result_data[agent_id][model_id]
                    self.log_debug(f'removed model {model_id} from agent {agent_id}')
                    return True
                else:
                    self.log_warning(f'model {model_id} could not be removed')
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
                    self.log_warning(f'link from (model {output_model_id} / output {output_name}) to (model {input_model_id} / input {input_name}) in agent {agent_id} could not be created')
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
                    self.log_warning(f'link from (model {output_model_id}:{output_name}) to (model {input_model_id}:{input_name}) in agent {agent_id} could not be removed')
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
                    self.log_warning(f'property {property_name} of model {model_id} in agent {agent_id} could not be set')
        return False

#endregion model

#region simulation

    def start_agent(self, agent_id):
        self.log_debug('starting start_agent')
        if self.is_existing_agent(agent_id):
            if self.is_agent_paused(agent_id):
                self.log_debug(f'agent {agent_id} already running but paused')
                if self.unpause_agent(agent_id):
                    self.log_debug(f'agent {agent_id} unpaused')
                    return True
            elif not self.is_agent_running(agent_id):
                p = multiprocessing.Process(target=self.agents[agent_id].run)
                self.agents_running[agent_id] = p
                p.start()
                self.log_debug(f'agent {agent_id} started')
                return True
            else:
                self.log_debug(f'agent {agent_id} is already running')
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
            else:
                self.log_debug(f'agent {agent_id} is not running')
        return False

    def kill_agent(self, agent_id):
        self.log_debug(f'starting kill_agent')
        if self.is_existing_agent(agent_id):
            if self.is_agent_running(agent_id):
                self.agents_running[agent_id].terminate()
                if self.is_agent_paused(agent_id):
                    self.agents_paused.remove(agent_id)
                del self.agents_running[agent_id]
                return True
            else:
                self.log_debug(f'agent {agent_id} is not running')
                return True
        return False

    def get_model_result(self, agent_id, model_id):
        self.log_debug(f'starting get_model_result')
        try:
            return self.result_data[agent_id][model_id]
        except KeyError:
            self.log_warning(f'no result data found for model {model_id} in agent {agent_id}')
            return None
    
    def get_model_results_newer_than(self, agent_id, model_id, run):
        try:
            cur_run = self.model_runs[agent_id][model_id]
            if run < cur_run:
                result = self.get_model_result(agent_id, model_id)
                return {'run': cur_run, 'result': result}
        except KeyError:
            self.log_warning(f'no model run found for {model_id} in {agent_id}')
        return None

#endregion simulation

#region util

    # Todo: @Simon: add function "get_status" to return ['running' || 'paused' || 'stopped']

    def is_existing_agent(self, agent_id):
        if agent_id in self.agents:
            return True
        self.log_debug(f'agent {agent_id} is not existing')
        return False

    def is_agent_running(self, agent_id):
        if agent_id in self.agents_running:
            return True
        return False

    def is_agent_paused(self, agent_id):
        if agent_id in self.agents_paused:
            return True
        return False

    def get_agent_status(self, agent_id):
        if self.is_agent_paused(agent_id):
            return "paused"
        if self.is_agent_running(agent_id):
            return "running"
        return "stopped"

    def get_agents_running(self):
        return list(self.agents_running)

    def get_agents(self):
        return list(self.agents.keys())

#endregion util

#region messaging

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
                self.handle_dead_order(msg)
            elif msg['order'] == 'data':
                self.handle_data_order(msg)
            elif msg['order'] == 'kill':
                self.handle_kill_order(msg)
        except KeyError:
            self.log_warning(f'message could not be handled correctly')
            self.log_warning(f'message = {msg}')

    def handle_dead_order(self, msg):
        agent_id = msg['agent']
        if self.is_agent_running(agent_id):
            self.agents_running[agent_id].terminate()
            self.log_debug(f'agent {agent_id} terminated')
            del self.agents_running[agent_id]
        if self.is_agent_paused(agent_id):
            self.agents_paused.remove(agent_id)
        self.log_debug(f'agent {agent_id} removed from running list')

    def handle_kill_order(self, msg):
        agent_id = msg['agent']
        self.kill_agent(agent_id)

    def handle_data_order(self, msg):
        agent_id = msg['agent']
        model_id = msg['model']
        data = msg['text']
        if not agent_id in self.result_data:
            self.result_data[agent_id] = {}
        if not model_id in self.result_data[agent_id]:
            self.result_data[agent_id][model_id] = {}

        if not agent_id in self.model_runs:
            self.model_runs[agent_id] = {}
        model_run = data[0]
        self.model_runs[agent_id][model_id] = model_run
        
        for name, result in data[1:]:
            self.result_data[agent_id][model_id][name] = result

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
            self.log_warning(f'no queue found for agent_id {agent_id}')
        return False

#endregion messaging