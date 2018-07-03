from Models.Technology.European_power_plant.V001.db.db_declarative import Base, Kraftwerk, Kraftwerkstyp, \
    Kraftwerksleistung, Brennstofftyp, Brennstoffpreis, Verguetung, Entsorgungspreis, Co2Preis

from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker
import datetime
import random


def create_dummy_data(session):

    # ################### Brennstofftyp #############################
    session.query(Brennstofftyp).delete()
    session.commit()

    for bst_info in [["Erdgas", 1.58],
                     ["Biomasse", 1.2],
                     ["Kernbrennstoff", 1.2],
                     ["Braunkohle", 2],
                     ["Steinkohle", 1.8],
                     ["None", 0]]:
        bst = Brennstofftyp(bezeichnung=bst_info[0],
                            co2emissFakt=bst_info[1])
        session.add(bst)
        try:
            session.commit()
        except exc.IntegrityError as e:
            print(e)
            session.rollback()

    # ################### Brennstoffpreis #############################
    session.query(Brennstoffpreis).delete()
    session.commit()

    bsts = session.query(Brennstofftyp).all()
    for bst in bsts:
        if bst.bezeichnung != "None":
            for _ in range(random.randint(1, 10)):
                bsp = Brennstoffpreis(fk_brennstofftyp=bst.id,
                                      long=random.random()*60 - 20,
                                      lat=random.random()*60 + 20,
                                      datetime=datetime.datetime.now()+random.randint(0, 60) *
                                               datetime.timedelta(days=30),
                                      preis=random.randint(500, 1500))
                session.add(bsp)
                try:
                    session.commit()
                except exc.IntegrityError as e:
                    print(e)
                    session.rollback()

    # ################### Kraftwerkstyp #############################
    session.query(Kraftwerkstyp).delete()
    session.commit()

    for kwt_info in [["Biomassekraftwerk", None, "Biomasse"],
                     ["Braunkohlekraftwerk", "alt", "Braunkohle"],
                     ["Braunkohlekraftwerk", "neu", "Braunkohle"],
                     ["Gasturbine", "absicherung", "Erdgas"],
                     ["Gasturbine", "peak", "Erdgas"],
                     ["Gaskombikraftwerk", "alt", "Erdgas"],
                     ["Gaskombikraftwerk", "neu", "Erdgas"],
                     ["Kernkraftwerk", None, "Kernbrennstoff"],
                     ["Laufwasserkraftwerk", None, "None"],
                     ["Photovoltaik", None, "None"],
                     ["Speicherwasserkraftwerk", None, "None"],
                     ["Steinkohlekraftwerk", "alt", "Steinkohle"],
                     ["Steinkohlekraftwerk", "neu", "Steinkohle"],
                     ["Windturbine", "offshore", "None"],
                     ["Windturbine", "onshore schwachwind", "None"],
                     ["Windturbine", "onshore starkwind", "None"]]:
        bst = session.query(Brennstofftyp).filter_by(bezeichnung=kwt_info[2]).first()
        kwt = Kraftwerkstyp(bezeichnung=kwt_info[0],
                            bezeichnung_subtyp=kwt_info[1],
                            fk_brennstofftyp=bst.id,
                            wirkungsgrad=random.randint(5, 10)/10,
                            spez_opex=random.randint(400, 800),
                            capex=random.randint(5, 8)/10,
                            p_typisch=random.randint(100, 1000),
                            spez_info="info...")
        session.add(kwt)
        try:
            session.commit()
        except exc.IntegrityError as e:
            print(e)
            session.rollback()

    # ################### Kraftwerk #############################
    session.query(Kraftwerk).delete()
    session.commit()

    kwts = session.query(Kraftwerkstyp).all()
    for i in range(100):
        kwt = random.choice(kwts)
        kw = Kraftwerk(bezeichnung=kwt.bezeichnung + "_" + str(i),
                       fk_kraftwerkstyp=kwt.id,
                       long=random.random() * 60 - 20,
                       lat=random.random() * 60 + 20)
        session.add(kw)
        try:
            session.commit()
        except exc.IntegrityError as e:
            print(e)
            session.rollback()

    # ################### Kraftwerksleistung #############################
    session.query(Kraftwerksleistung).delete()
    session.commit()

    kws = session.query(Kraftwerk).all()
    for kw in kws:
        for _ in range(random.randint(1, 3)):
            kwl = Kraftwerksleistung(fk_kraftwerk=kw.id,
                                     power_inst=random.randint(500, 1500),
                                     datetime=datetime.datetime.now()+random.randint(0, 20) *
                                              datetime.timedelta(days=365))
            session.add(kwl)
            try:
                session.commit()
            except exc.IntegrityError as e:
                print(e)
                session.rollback()

    # ################### Verguetungen #############################
    session.query(Verguetung).delete()
    session.commit()

    kwts = session.query(Kraftwerkstyp).all()
    for kwt in kwts:
        for _ in range(random.randint(1, 5)):
            verg = Verguetung(fk_kraftwerkstyp=kwt.id,
                              long=random.random() * 60 - 20,
                              lat=random.random() * 60 + 20,
                              datetime=datetime.datetime.now() + random.randint(0, 5) *
                                       datetime.timedelta(days=365),
                              beitrag=random.random()*150)
            session.add(verg)
            try:
                session.commit()
            except exc.IntegrityError as e:
                print(e)
                session.rollback()

    # ################### Entsorgungspreis #############################
    session.query(Entsorgungspreis).delete()
    session.commit()

    kwts = session.query(Kraftwerkstyp).all()
    for kwt in kwts:
        if kwt.brennstofftyp.bezeichnung != "None":
            for _ in range(random.randint(1, 3)):
                entp = Entsorgungspreis(fk_kraftwerkstyp=kwt.id,
                                        long=random.random() * 60 - 20,
                                        lat=random.random() * 60 + 20,
                                        datetime=datetime.datetime.now() + random.randint(0, 20) *
                                                 datetime.timedelta(days=365),
                                        preis=random.randint(100, 200))
                session.add(entp)
                try:
                    session.commit()
                except exc.IntegrityError as e:
                    print(e)
                    session.rollback()

    # ################### Co2Preis #############################
    session.query(Co2Preis).delete()
    session.commit()

    for i in range(50):
        co2p = Co2Preis(datetime=datetime.datetime.now() + random.randint(0, 10) * datetime.timedelta(days=365),
                        preis=random.randint(100, 200))
        session.add(co2p)
        try:
            session.commit()
        except exc.IntegrityError as e:
            print(e)
            session.rollback()
