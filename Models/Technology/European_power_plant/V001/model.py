from Models.Technology.European_power_plant.V001.db import Base, Kraftwerk, Kraftwerkstyp,Brennstofftyp, Brennstoffpreis, Verguetung, Entsorgungspreis, db_url
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker
import datetime, random

if __name__ == "__main__":
    engine = create_engine(db_url)
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()


    kw = session.query(Kraftwerk).first()

    r=5
    