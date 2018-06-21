import asyncio
from core.util import Input, Output, Property
from core.supermodel import Supermodel

class Model(Supermodel):

    def __init__(self, uuid, name: str):
        super(Model, self).__init__(uuid,name)

        self.outputs['text'] = Output({'name': 'Text'})
        self.properties['slide_amount'] = Property(1,int, {'name':'Slide Amount'})
        self.properties['window_size'] = Property(10,int, {'name':'Window Size'})
        self.properties['full_text'] = Property("Hello World! ",str, {'name': 'Text'})

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
