import asyncio
import os
import importlib
import logging
import errno

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

    def __init__(self, initial_value, property_type, info: dict):
        super(Property, self).__init__(info)
        self.property_type = property_type
        self.amend_value = None

        self.set_property(initial_value)

    def get_property(self):
        return self.items['value']

    def set_property(self, property_value):
        if type(property_value) != self.property_type:
            try:
                property_value = self.property_type(property_value)
                self.items['value'] = property_value
            except ValueError:
                raise
        else:
            self.items['value'] = property_value

    def set_amend_property(self, property_value):
        self.amend_value = property_value

    def amend(self):
        if self.amend_value:
            self.set_property(self.amend_value)
            self.amend_value = None
            return True
        return False

class CreateDirFileHandler(logging.FileHandler):
    def __init__(self, filename, mode='a', encoding=None, delay=0):
        self.create_dir(os.path.dirname(filename))
        super(CreateDirFileHandler,self).__init__(filename, mode, encoding, delay)

    def create_dir(self, path):
        try:
            os.makedirs(path, exist_ok=True)
        except TypeError:
            try:
                os.makedirs(path)
            except OSError as exc:
                if exc.errno == errno.EEXIST and os.path.isdir(path):
                    pass
                else: raise



def get_models():
    def _get_folders(path):
        dirs = os.listdir(path)
        dirs = filter(lambda x: os.path.isdir(path + '/' + x), dirs)
        dirs = filter(lambda x: x[0] != '_', dirs)
        return list(dirs)

    path = "Models"
    model_dict = dict()
    for topic in _get_folders(path):
        model_dict[topic] = dict()
        for model in _get_folders(path + '/' + topic):
            model_dict[topic][model] = dict()
            for version in _get_folders(path + '/' + topic + '/' + model):


                try:
                    mod = importlib.import_module(f"Models.{topic}.{model}.{version}.model").Model(1, '')
                    info = mod.get_info()
                    docks = list()
                    for direction in ['input', 'output']:
                        for port_key, port in info[direction + "s"].items():
                            port['key'] = port_key
                        ports = [port for key, port in info[direction + "s"].items()]
                        orientation = "left" if direction == "input" else "right"
                        docks.append({'direction': direction, 'orientation': orientation, 'ports': ports})
                    model_dict[topic][model][version] = {'docks': docks, 'properties': info["properties"]}
                except Exception as e:
                    print(f"Error in Models.{topic}.{model}.{version}.model ({e})")
    return model_dict