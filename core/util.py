import asyncio
import os
import importlib

class Port():
    def __init__(self, info: dict):
        self.items = dict()
        self.items['info'] = info

    def get_port_info(self):
        return self.items['info']


class Input(Port):

    def add_link(self, output_model, output_name: str):
        self.items['value'] = (output_model, output_name)
        
    def remove_link(self):
        if 'value' in self.items:
            del self.items['value']
    
    def get_input(self):
        try:
            o_mod = self.items['value'][0]
            o_nam = self.items['value'][1]
            return o_mod.outputs[o_nam].get_output()
        except KeyError:
            raise

class Output(Port):
    
    def clean_output(self):
        self.items['value'] = asyncio.Future()

    def set_output(self, value):
        self.items['value'].set_result(value)

    def get_output(self):
        return self.items['value']

class Property(Port):

    def __init__(self, initial_value, info: dict):
        super(Property, self).__init__(info)
        self.set_property(initial_value)
        self.amend_value = None

    def get_property(self):
        return self.items['value']

    def set_property(self, property_value):
        self.items['value'] = property_value

    def set_amend_property(self, property_value):
        self.amend_value = property_value

    def amend(self):
        if self.amend_value:
            self.items['value'] = self.amend_value
            self.amend_value = None





def get_models():
    def _get_folders(path):
        dirs = os.listdir(path)
        dirs = filter(lambda x: os.path.isdir(path + '/' + x), dirs)
        dirs = filter(lambda x: x[0] != '_', dirs)
        return list(dirs)

    path = os.path.dirname(os.path.realpath(__file__))
    model_dict = dict()
    for topic in _get_folders(path):
        model_dict[topic] = dict()
        for model in _get_folders(path + '/' + topic):
            model_dict[topic][model] = dict()
            for version in _get_folders(path + '/' + topic + '/' + model):
                model_dict[topic][model][version] = dict()


                try:
                    mod = importlib.import_module(f"Models.{topic}.{model}.{version}.model").Model(1, '')
                except Exception as e:
                    print(e)
                info = mod.get_info()
                input = info["inputs"]
                output = info["outputs"]
                docks = {'input': input, 'output': output}
                ################ so bekommen wir die daten
                docklist = list()
                for direction, dock in docks.items():
                    for port_key, port in dock.items():
                        port['key'] = port_key
                    orientation = "left" if direction == "input" else "right"
                    ports = [port for key, port in dock.items()]
                    dock = {'direction': direction, 'orientation': orientation, 'ports': ports}
                    docklist.append(dock)
                model_dict[topic][model][version] = {'docks': docklist, 'properties': info["properties"]}
    return model_dict