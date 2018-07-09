import asyncio
import os
import importlib
import logging
import errno
import time
import json


class Port():
    def __init__(self, name, unit='undefined', info='-', example='-', **kwargs):
        self.items = dict()
        self.items['info'] = kwargs if kwargs is not None else dict()
        self.items['info']['name'] = name
        self.items['info']['unit'] = unit
        self.items['info']['info'] = info
        self.items['info']['example'] = example

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

    def __init__(self, name, default=0, data_type=int, unit='undefined', info='-', example='-', **kwargs):
        super(Property, self).__init__(name, unit=unit, info=info, example=example, **kwargs)
        self.property_type = data_type
        self.amend_value = None

        self.items['info']['default'] = default
        self.items['info']['data_type'] = str(data_type)

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
                else:
                    raise
