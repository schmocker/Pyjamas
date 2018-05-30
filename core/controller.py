import importlib
import uuid
import multiprocessing
import json
import time
from threading import Thread

class Controller():

    def __init__(self):
        self.agents = {}
        self.agents_running = []
        self.controller_queue = multiprocessing.Queue()
        self.agent_queues = {}
        self.thread_running = False

    def add_agent(self, agent_id, agent_name: str):
        agent_queue = multiprocessing.Queue()
        self.agent_queues[agent_id] = agent_queue
        a = importlib.import_module("core.agent").Agent(agent_id, agent_name, self.controller_queue, agent_queue)
        self.agents[agent_id] = a
        if not self.thread_running:
            self.start()

    def remove_agent(self, agent_id: str):
        if self.is_agent_running(agent_id):
            self.kill_agent(agent_id)
        del self.agent_queues[agent_id]
        del self.agents[agent_id]
        if len(self.agents) <= 0:
            self.stop()
    
    def add_model(self, agent_id, model_path: str, model_id, model_name: str):
        if not self.is_agent_running(agent_id):
            mod = importlib.import_module(f"Models.{model_path}").Model(model_id,model_name)
            self.agents[agent_id].add_model(mod)
            return model_id

    def remove_model(self, agent_id, model_id):
        if not self.is_agent_running(agent_id):
            self.agents[agent_id].remove_model(model_id)
    
    def link_models(self, agent_id, output_model_id, output_name: str, input_model_id, input_name: str):
        if not self.is_agent_running(agent_id):
            self.agents[agent_id].link_models(output_model_id,output_name,input_model_id,input_name)

    def set_property(self, agent_id, model_id, property_name: str, property_value):
        if self.is_agent_running(agent_id):
            self.send_set_property_order(agent_id,model_id,property_name,property_value)
        else:
            self.agents[agent_id].set_property(model_id,property_name,property_value)

    def start_agent(self, agent_id):
        if not self.is_agent_running(agent_id):
            self.agents_running.append(agent_id)
            self.agents[agent_id].start()

    def stop_agent(self, agent_id):
        if self.is_agent_running(agent_id):
            self.send_stop_order(agent_id)

    def kill_agent(self, agent_id):
        if self.is_agent_running(agent_id):
            self.send_kill_order(agent_id)

    def is_agent_running(self, agent_id):
        if agent_id in self.agents_running:
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
        while self.thread_running or self.agents_running:
            try:
                msg = self.controller_queue.get(True)
                self.handle_input(msg)
            except Exception as e:
                print(e)

    def handle_input(self, msg):
        if msg["order"] == "dead":
            self.agents_running.remove(msg["agent"])

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
        self.agent_queues[agent_id].put(order)

    def send_stop_order(self, agent_id):
        order = {}
        order["order"] = "stop"
        order["agent"] = agent_id
        self.agent_queues[agent_id].put(order)

    def send_kill_order(self, agent_id):
        order = {}
        order["order"] = "kill"
        order["agent"] = agent_id
        self.agent_queues[agent_id].put(order)
