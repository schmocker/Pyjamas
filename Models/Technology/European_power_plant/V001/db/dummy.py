from Models.Technology.European_power_plant.V001.db import Base, Kraftwerk, Kraftwerkstyp, Brennstofftyp, Brennstoffpreis, Verguetung, Entsorgungspreis, db_url

from sqlalchemy import create_engine, exc
from sqlalchemy.orm import sessionmaker
import datetime, random


if __name__ == "__main__":
    engine = create_engine(db_url)
    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    session = DBSession()






    ################### Brennstofftyp #############################
    #session.query(Brennstofftyp).delete()
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
                       lat=random.random()*150,
                       power_inst=random.random()*1500)
        session.add(kw)
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
        kw = Brennstoffpreis(fk_brennstofftyp=bst.id,
                             long=random.random()*200,
                             lat=random.random()*150,
                             datetime=datetime.datetime.now(),
                             preis=1500)
        session.add(kw)
        try:
            session.commit()
        except exc.IntegrityError as e:
            print(e)
            session.rollback()


