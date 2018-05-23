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
        self.queue = multiprocessing.Queue()
        self.thread_running = False

    def add_agent(self, agent_name: str):
        a = importlib.import_module("pyjama.core.agent").Agent(agent_name, self.queue)
        self.agents[agent_name] = a
        if not self.thread_running:
            self.start()

    def remove_agent(self, agent_name: str):
        if self.is_agent_running(agent_name):
            self.kill_agent(agent_name)
        del self.agents[agent_name]
        if len(self.agents) <= 0:
            self.stop()
    
    def add_model(self, agent_name: str, model_path: str, model_name: str):
        if not self.is_agent_running(agent_name):
            i = uuid.uuid4()
            mod = importlib.import_module(f"pyjama.models.{model_path}").Model(i,model_name)
            self.agents[agent_name].add_model(mod)
            return i

    def remove_model(self, agent_name: str, model_id):
        if not self.is_agent_running(agent_name):
            self.agents[agent_name].remove_model(model_id)
    
    def link_models(self, agent_name: str, output_model_id, output_name: str, input_model_id, input_name: str):
        if not self.is_agent_running(agent_name):
            self.agents[agent_name].link_models(output_model_id,output_name,input_model_id,input_name)

    def set_property(self, agent_name: str, model_id, property_name: str, property_value):
        if self.is_agent_running(agent_name):
            self.send_set_property_order(agent_name,model_id,property_name,property_value)
        else:
            self.agents[agent_name].set_property(model_id,property_name,property_value)

    def start_agent(self, agent_name: str):
        if not self.is_agent_running(agent_name):
            self.agents_running.append(agent_name)
            self.agents[agent_name].start()

    def stop_agent(self, agent_name: str):
        if self.is_agent_running(agent_name):
            self.send_stop_order(agent_name)

    def kill_agent(self, agent_name: str):
        if self.is_agent_running(agent_name):
            self.send_kill_order(agent_name)

    def is_agent_running(self, agent_name: str):
        if agent_name in self.agents_running:
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
        while self.thread_running:
            if not self.queue.empty():
                try:
                    msg = self.queue.get(False)
                    if msg["order"] == "dead":
                        self.handle_input(msg) 
                    else:
                        self.queue.put(msg)
                except Exception:
                    pass
            time.sleep(.1)

    def handle_input(self, msg):
        if msg["order"] == "dead":
            self.agents_running.remove(msg["agent"])

    # orders

    def send_set_property_order(self, agent_name, model_id, property_name, property_value):
        text = {}
        text["property_name"] = property_name
        text["property_value"] = property_value

        order = {}
        order["order"] = "prop"
        order["agent"] = agent_name
        order["model"] = model_id
        order["text"] = text
        self.queue.put(order)

    def send_stop_order(self, agent_name):
        order = {}
        order["order"] = "stop"
        order["agent"] = agent_name
        self.queue.put(order)

    def send_kill_order(self, agent_name):
        order = {}
        order["order"] = "kill"
        order["agent"] = agent_name
        self.queue.put(order)
