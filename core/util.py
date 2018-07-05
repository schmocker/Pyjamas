import asyncio
import os
import importlib
import logging
import errno
import time

class Port():
    def __init__(self, name='', unit='-', **kwargs):
        self.items = dict()
        self.items['info'] = kwargs if kwargs is not None else dict()
        self.items['info']['name'] = name
        self.items['info']['unit'] = unit

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

    def _init_(self, default='', data_type=str, name='', unit='-', example='-', **kwargs):
        super(Property, self).__init__(name=name, unit=unit, example=example, **kwargs)
        self.property_type = data_type
        self.amend_value = None

        self.set_property(default)

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
        if self.amend_value != None:
            try:
                self.set_property(self.amend_value)
                self.amend_value = None
                return True
            except ValueError:
                self.amend_value = None
                raise
        self.amend_value = None
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


def get_model_info(p, t, m, v):
    def gen_dock(direction, in_out_puts):
        orientation = "left" if direction == "input" else "right"
        ports = [gen_port(key, in_out_put) for key, in_out_put in in_out_puts.items()]
        return {'direction': direction, 'orientation': orientation, 'ports': ports}

    def gen_port(key, in_out_put):
        in_out_put['key'] = key
        return in_out_put

    try:
        info = importlib.import_module(f"{p}.{t}.{m}.{v}.model").Model(1, '').get_info()
        docks = [gen_dock(direction, info[direction + "s"]) for direction in ['input', 'output']]
        return {'docks': docks, 'properties': info["properties"]}
    except Exception as e:
        print(f" --> Error updating {p}.{t}.{m}.{v}.model ({e})")
