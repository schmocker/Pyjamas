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
    bsp = session.query(Brennstoffpreis).filter_by(fk_brennstofftyp=kw.kraftwerkstyp.brennstofftyp.id).all()

    lat = [b.lat for b in bsp]
    long = [b.long for b in bsp]
    datetime = [b.datetime for b in bsp]
    preis = [b.preis for b in bsp]

    r=5
    