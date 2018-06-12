import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from Models.Technology.European_power_plant.V001.db.config import db_url
Base = declarative_base()



class Brennstofftyp(Base):
    __tablename__ = 'brennstofftyp'
    # declare columns
    id = Column(Integer, primary_key=True)
    bezeichnung = Column(String(250), nullable=False, unique=True)
    co2emissFakt = Column(Float, nullable=False)

class Brennstoffpreis(Base):
    __tablename__ = 'brennstoffpreis'
    # declare columns
    id = Column(Integer, primary_key=True)
    fk_brennstofftyp = Column(Integer, ForeignKey('brennstofftyp.id', ondelete="CASCADE"))
    long = Column(Float, nullable=False)
    lat = Column(Float, nullable=False)
    datetime = Column(DateTime, nullable=False)
    preis = Column(Float, nullable=False)
    # declare relations
    brennstofftyp = relationship("Brennstofftyp", foreign_keys=[fk_brennstofftyp],
                            backref=backref("brennstoffpreise",cascade="all, delete-orphan", lazy=True))

class Kraftwerkstyp(Base):
    __tablename__ = 'kraftwerkstyp'
    # declare columns
    id = Column(Integer, primary_key=True)
    bezeichnung = Column(String(250), nullable=False, unique=True)
    fk_brennstofftyp = Column(Integer, ForeignKey('brennstofftyp.id', ondelete="CASCADE"))
    wirkungsgrad = Column(Float)
    spez_opex = Column(Float, nullable=False)
    capex = Column(Float, nullable=False)
    # declare relations
    brennstofftyp = relationship("Brennstofftyp", foreign_keys=[fk_brennstofftyp],
                            backref=backref("kraftwerkstypen",cascade="all, delete-orphan", lazy=True))

class Kraftwerk(Base):
    __tablename__ = 'kraftwerk'
    # declare columns
    id = Column(Integer, primary_key=True)
    bezeichnung = Column(String(250), nullable=False)
    fk_kraftwerkstyp = Column(Integer, ForeignKey('kraftwerkstyp.id', ondelete="CASCADE"))
    long = Column(Float, nullable=False)
    lat = Column(Float, nullable=False)
    power_inst = Column(Float, nullable=False)
    datetime = Column(DateTime, nullable=False)
    spez_info = Column(Text)
    # declare relations
    kraftwerkstyp = relationship("Kraftwerkstyp", foreign_keys=[fk_kraftwerkstyp],
                            backref=backref("kraftwerke",cascade="all, delete-orphan", lazy=True))

    

class Verguetung(Base):
    __tablename__ = 'verguetung'
    # declare columns
    id = Column(Integer, primary_key=True)
    fk_kraftwerkstyp = Column(Integer, ForeignKey('kraftwerkstyp.id', ondelete="CASCADE"))
    long = Column(Float, nullable=False)
    lat = Column(Float, nullable=False)
    datetime = Column(DateTime, nullable=False)
    breitrag = Column(Float, nullable=False)
    # declare relations
    kraftwerkstyp = relationship("Kraftwerkstyp", foreign_keys=[fk_kraftwerkstyp],
                            backref=backref("verguetungen",cascade="all, delete-orphan", lazy=True))

class Entsorgungspreis(Base):
    __tablename__ = 'entsorgungspreis'
    # declare columns
    id = Column(Integer, primary_key=True)
    fk_kraftwerkstyp = Column(Integer, ForeignKey('kraftwerkstyp.id', ondelete="CASCADE"))
    long = Column(Float, nullable=False)
    lat = Column(Float, nullable=False)
    datetime = Column(DateTime, nullable=False)
    preis = Column(Float, nullable=False)
    # declare relations
    kraftwerkstyp = relationship("Kraftwerkstyp", foreign_keys=[fk_kraftwerkstyp],
                            backref=backref("entsorgungspreise",cascade="all, delete-orphan", lazy=True))


class Co2Preis(Base):
    __tablename__ = 'co2preis'
    # declare columns
    id = Column(Integer, primary_key=True)
    long = Column(Float, nullable=False)
    lat = Column(Float, nullable=False)
    datetime = Column(DateTime, nullable=False)
    preis = Column(Float, nullable=False)





if __name__ == "__main__":
    engine = create_engine(db_url)

    try:
        for tbl in Base.metadata.sorted_tables:
            tbl.drop(engine)
    except:
        pass

    # Create all tables in the engine. This is equivalent to "Create Table"
    # statements in raw SQL.
    Base.metadata.create_all(engine)
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()