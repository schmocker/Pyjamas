from Models.Technology.European_power_plant.V001.db.db_declarative import Base, Kraftwerk, Kraftwerkstyp, \
    Kraftwerksleistung, Brennstofftyp, Brennstoffpreis, Verguetung, Entsorgungspreis, Co2Preis

from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker
import datetime
import random


def create_dummy_data(session):

    ################### Brennstofftyp #############################
    session.query(Brennstofftyp).delete()
    session.commit()

    for bst_info in [["Erdgas",1.58],["None",0]]:
        bst = Brennstofftyp(bezeichnung=bst_info[0],
                            co2emissFakt=bst_info[1])
        session.add(bst)
        try:
            session.commit()
        except exc.IntegrityError as e:
            print(e)
            session.rollback()

    ################### Brennstoffpreis #############################
    session.query(Brennstoffpreis).delete()
    session.commit()

    bsts = session.query(Brennstofftyp).all()
    for i in range(50):
        bst = random.choice(bsts)
        bsp = Brennstoffpreis(fk_brennstofftyp=bst.id,
                              long=random.random()*200,
                              lat=random.random()*150,
                              datetime=datetime.datetime.now(),
                              preis=1500)
        session.add(bsp)
        try:
            session.commit()
        except exc.IntegrityError as e:
            print(e)
            session.rollback()


    ################### Kraftwerkstyp #############################
    session.query(Kraftwerkstyp).delete()
    session.commit()

    for kwt_info in [["Gasturbine","Erdgas"],["Gaskombikraftwerk","Erdgas"],["Windturbine","None"],["PV","None"]]:

        bst = session.query(Brennstofftyp).filter_by(bezeichnung=kwt_info[1]).first()
        kwt = Kraftwerkstyp(bezeichnung=kwt_info[0],
                            fk_brennstofftyp=bst.id,
                            wirkungsgrad=0.8,
                            spez_opex=500,
                            capex=0.4)
        session.add(kwt)
        try:
            session.commit()
        except exc.IntegrityError as e:
            print(e)
            session.rollback()


    ################### Kraftwerk #############################
    session.query(Kraftwerk).delete()
    session.commit()

    kwts = session.query(Kraftwerkstyp).all()
    for i in range(50):
        kwt = random.choice(kwts)
        kw = Kraftwerk(bezeichnung=kwt.bezeichnung + "_" + str(i),
                       fk_kraftwerkstyp=kwt.id,
                       long=random.random()*200,
                       lat=random.random()*150)
        session.add(kw)
        try:
            session.commit()
        except exc.IntegrityError as e:
            print(e)
            session.rollback()


    ################### Kraftwerksleistung #############################
    session.query(Kraftwerksleistung).delete()
    session.commit()

    kws = session.query(Kraftwerk).all()
    for kw in kws:
        kwl = Kraftwerksleistung(fk_kraftwerk=kw.id,
                                 power_inst=random.random()*1500,
                                 datetime=datetime.datetime.now())
        session.add(kwl)

        kwl = Kraftwerksleistung(fk_kraftwerk=kw.id,
                                 power_inst=random.random()*1500,
                                 datetime=datetime.datetime.now())
        session.add(kwl)

        kwl = Kraftwerksleistung(fk_kraftwerk=kw.id,
                                 power_inst=random.random()*1500,
                                 datetime=datetime.datetime.now())
        session.add(kwl)

        try:
            session.commit()
        except exc.IntegrityError as e:
            print(e)
            session.rollback()

    ################### Verguetungen #############################
    session.query(Verguetung).delete()
    session.commit()

    kwts = session.query(Kraftwerkstyp).all()
    for i in range(50):
        kwt = random.choice(kwts)
        verg = Verguetung(fk_kraftwerkstyp=kwt.id,
                          long=random.random()*200,
                          lat=random.random()*150,
                          datetime=datetime.datetime.now(),
                          breitrag=random.random()*150)
        session.add(verg)
        try:
            session.commit()
        except exc.IntegrityError as e:
            print(e)
            session.rollback()

    ################### Entsorgungspreis #############################
    session.query(Entsorgungspreis).delete()
    session.commit()

    kwts = session.query(Kraftwerkstyp).all()
    for i in range(50):
        kwt = random.choice(kwts)
        entp = Entsorgungspreis(fk_kraftwerkstyp=kwt.id,
                                long=random.random()*200,
                                lat=random.random()*150,
                                datetime=datetime.datetime.now(),
                                preis=random.random()*150)
        session.add(entp)
        try:
            session.commit()
        except exc.IntegrityError as e:
            print(e)
            session.rollback()

    ################### Co2Preis #############################
    session.query(Co2Preis).delete()
    session.commit()

    for i in range(50):
        co2p = Co2Preis(long=random.random()*200,
                       lat=random.random()*150,
                       datetime=datetime.datetime.now(),
                       preis=random.random()*150)
        session.add(co2p)
        try:
            session.commit()
        except exc.IntegrityError as e:
            print(e)
            session.rollback()
