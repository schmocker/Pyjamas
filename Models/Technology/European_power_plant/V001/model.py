from core import Supermodel
from Models.Technology.European_power_plant.V001.db import Base, Kraftwerk, Kraftwerkstyp,Brennstofftyp,\
    Brennstoffpreis, Verguetung, Entsorgungspreis, Co2Preis, create_dummy_data

from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker
import datetime, random, os

class Model(Supermodel):
    # model constructor
    def __init__(self, id, name: str):
        # instantiate supermodel
        super(Model, self).__init__(id, name)


def start_db():
    db_path = 'db/powerplants.db'
    if not os.path.isfile(db_path):
        open(db_path, 'a').close()

    # an engine is the real DB
    engine = create_engine('sqlite:///'+db_path)

    # delete all tables
    Base.metadata.drop_all(engine)

    # create all tables
    Base.metadata.create_all(engine)

    # a session is used to communicate with the DB
    Base.metadata.bind = engine
    session = sessionmaker(bind=engine)()

    # create dummy data
    create_dummy_data(session)

    return session


if __name__ == "__main__":
    db = start_db()

    kw = db.query(Kraftwerk).first()

    r=5
