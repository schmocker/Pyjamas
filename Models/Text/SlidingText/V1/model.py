import asyncio
from pyjamas_core.util import Input, Output, Property
from pyjamas_core.supermodel import Supermodel

class Model(Supermodel):
    """outputs a string representing a sliding window on the full_text property
    """

    def __init__(self, uuid, name: str):
        super(Model, self).__init__(uuid,name)

        self.outputs['text'] = Output('Text')
        self.properties['slide_amount'] = Property('Slide Amount', default=1, data_type=int)
        self.properties['window_size'] = Property('Window Size', default=10, data_type=int)
        self.properties['full_text'] = Property('Text', default="Hello World! ", data_type=str)

        self.curr_pos = 0

    async def func_peri(self, prep_to_peri=None):
        full_text = self.get_property('full_text')
        window_size = self.get_property('window_size')

        if self.curr_pos >= len(full_text):
            self.curr_pos = self.curr_pos - len(full_text)

        end_pos = self.curr_pos + window_size

        if end_pos >= len(full_text):

            real_end_pos = end_pos - len(full_text)

            first_part = full_text[self.curr_pos:]
            second_part = full_text[:real_end_pos]

            window_text = f"{first_part}{second_part}"

        else:
            window_text = full_text[self.curr_pos:end_pos]

        self.set_output("text", window_text)

    async def func_post(self, peri_to_post=None):
        
        slide_amount = self.get_property('slide_amount')
        self.curr_pos += slide_amount
