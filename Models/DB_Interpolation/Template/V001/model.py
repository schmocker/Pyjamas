from core import Supermodel
from core.util import Input, Output, Property

from flask import Markup
import markdown2
import os
from pathlib import Path

from Models.Technology.European_power_plant.V001.db import Base, Kraftwerk, Kraftwerkstyp, Brennstofftyp, \
    Brennstoffpreis, Verguetung, Entsorgungspreis, db_url
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker
import datetime, random


# define the model class and inherit from class "Supermodel"
class Model(Supermodel):
    # model constructor
    def __init__(self, id, name: str):
        # instantiate supermodel
        super(Model, self).__init__(id, name)

        # define inputs
        self.inputs['v'] = Input({'name': 'wind speed'})
        self.inputs['dir'] = Input({'name': 'wind direction'})

        # define outputs
        self.outputs['p_el'] = Output({'name': 'electrical power'})
        self.outputs['f_rot'] = Output({'name': 'rotor frequency'})

        # define properties
        self.properties['h_hub'] = Property(10, {'name': 'hub height'})


        # define persistent variables
        self.pers_variable_0 = 5

    async def func_birth(self):
        if __name__ == "__main__":
            engine = create_engine(db_url)
            Base.metadata.bind = engine
            DBSession = sessionmaker(bind=engine)
            session = DBSession()

            kw = session.query(Kraftwerk).first()

    async def func_prep(self):
        # calculate something
        prep_result = 3 * 5
        # pass values to peri function
        return prep_result

    async def func_peri(self, prep_to_peri=None):
        prep_result = prep_to_peri
        # get inputs
        in1 = await self.get_input('v')
        in2 = await self.get_input('dir')

        # calculate something
        # One can declare custom functions (eg: see end of file)
        # If you declare them "async" you will have to "await" them (like "extremely_complex_calculation")
        # Else one could declare "normal" (blocking) functions as well (like "complex_calculation")
        out1 = prep_result * self.complex_calculation(in1)
        out2 = await self.extremely_complex_calculation(in1, in2)

        # set output
        self.set_output("p_el", out1)
        self.set_output("f_rot", out2)

        # pass values to post function
        outputs = {'out1': out1, 'out2': out2}
        return outputs

    async def func_post(self, peri_to_post=None):
        outputs = peri_to_post
        # do something with the values (eg: overwrite persistent variable)
        self.pers_variable_0 = outputs['out1']

    async def func_death(self):
        print("I am dying! Bye bye!")

    # define additional methods (normal)
    def complex_calculation(self, speed):
        speed_cut = speed / self.pers_variable_0
        return speed_cut

    # define additional methods (async)
    async def extremely_complex_calculation(self, speed, time):
        distance = speed * time / self.pers_variable_0
        return distance


    ######### TODO:
    @property
    def description(self):
        script_dir = os.path.dirname(__file__)
        abs_file_path = Path(os.path.join(script_dir, 'README.md'))
        if abs_file_path.exists():
            txt = open(abs_file_path, 'r', encoding="utf8").read()
            mkdwn = markdown2.markdown(txt, extras=['extra', 'fenced-code-blocks'])
            return Markup(mkdwn)
        else:
            return ""

