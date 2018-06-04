import asyncio

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
        super(Property, self).__init__(dict)
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