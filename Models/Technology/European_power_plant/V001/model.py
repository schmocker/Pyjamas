from core import Supermodel
from Models.Technology.European_power_plant.V001.db import Base, Kraftwerk, Kraftwerkstyp,Brennstofftyp, Brennstoffpreis, Verguetung, Entsorgungspreis, db_url, Co2Preis
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker
import datetime, random

class Model(Supermodel):
    # model constructor
    def __init__(self, id, name: str):
        # instantiate supermodel
        super(Model, self).__init__(id, name)

if __name__ == "__main__":
    engine = create_engine(db_url)
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()


    kw = session.query(Kraftwerk).first()

    r=5
    