from sqlalchemy import Column, ForeignKey, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

# Base is the superclass of each table
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
    datetime = Column(Integer, nullable=False)
    preis = Column(Float, nullable=False)
    # declare relations
    brennstofftyp = relationship("Brennstofftyp", foreign_keys=[fk_brennstofftyp],
                                 backref=backref("brennstoffpreise", cascade="all, delete-orphan", lazy=True))


class Kraftwerkstyp(Base):
    __tablename__ = 'kraftwerkstyp'
    # declare columns
    id = Column(Integer, primary_key=True)
    bezeichnung = Column(String(250), nullable=False)
    bezeichnung_subtyp = Column(String(250))
    fk_brennstofftyp = Column(Integer, ForeignKey('brennstofftyp.id', ondelete="CASCADE"))
    wirkungsgrad = Column(Float)
    opex = Column(Float, nullable=False)
    capex = Column(Float, nullable=False)
    p_typisch = Column(Float)
    spez_info = Column(Text)
    # declare relations
    brennstofftyp = relationship("Brennstofftyp", foreign_keys=[fk_brennstofftyp],
                                 backref=backref("kraftwerkstypen", cascade="all, delete-orphan", lazy=True))


class Kraftwerk(Base):
    __tablename__ = 'kraftwerk'
    # declare columns
    id = Column(Integer, primary_key=True)
    bezeichnung = Column(String(250), nullable=False)
    fk_kraftwerkstyp = Column(Integer, ForeignKey('kraftwerkstyp.id', ondelete="CASCADE"))
    long = Column(Float, nullable=False)
    lat = Column(Float, nullable=False)
    # declare relations
    kraftwerkstyp = relationship("Kraftwerkstyp", foreign_keys=[fk_kraftwerkstyp],
                                 backref=backref("kraftwerke", cascade="all, delete-orphan", lazy=True))


class Kraftwerksleistung(Base):
    __tablename__ = 'kraftwerksleistung'
    # declare columns
    id = Column(Integer, primary_key=True)
    fk_kraftwerk = Column(Integer, ForeignKey('kraftwerk.id', ondelete="CASCADE"))
    power_inst = Column(Float, nullable=False)
    datetime = Column(Integer, nullable=False)
    # declare relations
    kraftwerk = relationship("Kraftwerk", foreign_keys=[fk_kraftwerk],
                             backref=backref("kraftwerksleistungen", cascade="all, delete-orphan", lazy=True))


class Entsorgungspreis(Base):
    __tablename__ = 'entsorgungspreis'
    # declare columns
    id = Column(Integer, primary_key=True)
    fk_kraftwerkstyp = Column(Integer, ForeignKey('kraftwerkstyp.id', ondelete="CASCADE"))
    long = Column(Float, nullable=False)
    lat = Column(Float, nullable=False)
    datetime = Column(Integer, nullable=False)
    preis = Column(Float, nullable=False)
    # declare relations
    kraftwerkstyp = relationship("Kraftwerkstyp", foreign_keys=[fk_kraftwerkstyp],
                                 backref=backref("entsorgungspreise", cascade="all, delete-orphan", lazy=True))


class Co2Preis(Base):
    __tablename__ = 'co2preis'
    # declare columns
    id = Column(Integer, primary_key=True)
    datetime = Column(Integer, nullable=False)
    preis = Column(Float, nullable=False)
