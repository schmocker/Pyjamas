from Models.Technology.European_power_plant.V001.db.db_declarative import Base, Brennstofftyp, Brennstoffpreis, \
    Kraftwerkstyp, Kraftwerk, Kraftwerksleistung, VarOpex, Capex, Entsorgungspreis, Co2Preis

# imports for database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import exc

# general imports
from dotenv import load_dotenv
import random
import time


# ------------------------- define paths ----------------------------------
db_path = 'sqlite:///pyjamas_powerplants_dummy'

# ------------------------- create database  ------------------------------------
load_dotenv()

# an engine is the real DB
engine = create_engine(db_path)

# delete all tables
Base.metadata.drop_all(engine)
# create all tables
Base.metadata.create_all(engine)
# a session is used to communicate with the DB
Base.metadata.bind = engine
session = sessionmaker(bind=engine)()


# ################### Brennstofftyp #############################
session.query(Brennstofftyp).delete()
session.commit()

for bst_info in [["Erdgas", 0.000000056],
                 ["Biomasse", 0.000000004],
                 ["Kernbrennstoff", 0],
                 ["Braunkohle", 0.0000001],
                 ["Steinkohle", 0.000000095],
                 ["None", 0],
                 ["Oel", 0.000000078],
                 ["Weitere RES", 0.000000004],
                 ["Weitere nonRES", 0.000000056]]:

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
                                  datetime=int(time.time())+random.randint(0, 60) * 30*24*60*60,
                                  preis=random.randint(1, 20)/10**9)
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
                 ["Windturbine", "onshore starkwind", "None"],
                 ["Oelkraftwerk", None, "Oel"],
                 ["Weitere RES", None, "Weitere RES"],
                 ["Weitere nonRES", None, "Weitere nonRES"]]:

    bst = session.query(Brennstofftyp).filter_by(bezeichnung=kwt_info[2]).first()
    kwt = Kraftwerkstyp(bezeichnung=kwt_info[0],
                        bezeichnung_subtyp=kwt_info[1],
                        fk_brennstofftyp=bst.id,
                        wirkungsgrad=random.randint(5, 10)/10,
                        p_typisch=random.randint(5, 1500)*10**9,
                        spez_info="{'NH': 100, 'Z0': 0.1}")
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
                                 power_inst=random.randint(1000, 50000)*10**9,
                                 datetime=int(time.time()) + random.randint(0, 20) * 365*24*60*60)
        session.add(kwl)
try:
    session.commit()
except exc.IntegrityError as e:
    print(e)
    session.rollback()

# ################### VarOpex ######################################
session.query(VarOpex).delete()
session.commit()

kwts = session.query(Kraftwerkstyp).all()
for kwt in kwts:
    for i in range(2):
        var_opex = VarOpex(fk_kraftwerkstyp=kwt.id,
                           datetime=int(time.time()) + i * 20 * 365*24*60*60,  # today and in 20 years
                           preis=random.randint(1, 50)/1000)
        session.add(var_opex)
try:
    session.commit()
except exc.IntegrityError as e:
    print(e)
    session.rollback()

# ################### Capex ########################################
session.query(Capex).delete()
session.commit()

kwts = session.query(Kraftwerkstyp).all()
for kwt in kwts:
    for i in range(2):
        capex = Capex(fk_kraftwerkstyp=kwt.id,
                      datetime=int(time.time()) + i * 20 * 365*24*60*60,  # today and in 20 years
                      preis=random.randint(500, 3000))
        session.add(capex)
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
                                    datetime=int(time.time()) + random.randint(0, 20) * 365*24*60*60,
                                    preis=0)
            session.add(entp)
try:
    session.commit()
except exc.IntegrityError as e:
    print(e)
    session.rollback()

# ################### Co2Preis #############################
session.query(Co2Preis).delete()
session.commit()

for i in range(4):
    co2p = Co2Preis(datetime=int(time.time()) + i * 10 * 365*24*60*60,
                    preis=random.randint(20, 80)/1000)
    session.add(co2p)
try:
    session.commit()
except exc.IntegrityError as e:
    print(e)
    session.rollback()
