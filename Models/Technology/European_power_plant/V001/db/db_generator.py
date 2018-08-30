from Models.Technology.European_power_plant.V001.db import Base, Brennstofftyp, Brennstoffpreis, Kraftwerkstyp, \
    Kraftwerk, Kraftwerksleistung, VarOpex, Capex, Entsorgungspreis, Co2Preis

# imports for database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import exc

# general imports
from dotenv import load_dotenv
from os import environ

# pandas for reading excel files
import pandas as pd

# ------------------------- define data source ----------------------------------
source_file = 'Data.xlsx'

# ------------------------- create database  ------------------------------------
load_dotenv()

db_path = environ.get("KW_DB_new")
# an engine is the real DB
engine = create_engine(db_path)

# delete all tables
Base.metadata.drop_all(engine)
# create all tables
Base.metadata.create_all(engine)
# a session is used to communicate with the DB
Base.metadata.bind = engine
session = sessionmaker(bind=engine)()


# ------------------------- read excel ------------------------------------------
BSP = pd.read_excel(source_file, sheet_name='BSP')  # Brennstoffpreise
BST = pd.read_excel(source_file, sheet_name='BST')  # Brennstofftypen
CAPEX = pd.read_excel(source_file, sheet_name='CAPEX')  # CAPEX
CO2 = pd.read_excel(source_file, sheet_name='CO2')  # Co2-Preise
ENTS = pd.read_excel(source_file, sheet_name='ENTS')  # Entsorgungspreise
KW = pd.read_excel(source_file, sheet_name='KW')  # Kraftwerke
KWL = pd.read_excel(source_file, sheet_name='KWL')  # Kraftwerksleistungen
KWT = pd.read_excel(source_file, sheet_name='KWT')  # Kraftwerkstypen
OPEX = pd.read_excel(source_file, sheet_name='OPEX')  # Variabler Opex


# ------------------------- fill database ---------------------------------------

# ################### Brennstofftyp #############################
session.query(Brennstofftyp).delete()
session.commit()

for i, _ in BST.iterrows():
    bst = Brennstofftyp(id=int(BST['id'][i]),
                        bezeichnung=BST['bezeichnung'][i],
                        co2emissFakt=BST['co2EmissFaktor'][i]
                        )
    session.add(bst)
try:
    session.commit()
except exc.IntegrityError as e:
    print(e)
    session.rollback()

# ################### Brennstoffpreis #############################
session.query(Brennstoffpreis).delete()
session.commit()

for i, _ in BSP.iterrows():
    bsp = Brennstoffpreis(id=int(BSP['id'][i]),
                          fk_brennstofftyp=int(BSP['fk_brennstofftyp'][i]),
                          long=BSP['long'][i],
                          lat=BSP['lat'][i],
                          datetime=int(BSP['unix timestamp'][i]),
                          preis=BSP['preis'][i]
                          )
    session.add(bsp)
try:
    session.commit()
except exc.IntegrityError as e:
    print(e)
    session.rollback()

# ################### Kraftwerkstyp #############################
session.query(Kraftwerkstyp).delete()
session.commit()

for i, _ in KWT.iterrows():
    kwt = Kraftwerkstyp(id=int(KWT['id'][i]),
                        bezeichnung=KWT['bezeichnung'][i],
                        bezeichnung_subtyp=KWT['bezeichnung_subtyp'][i],
                        fk_brennstofftyp=int(KWT['fk_brennstofftyp'][i]),
                        wirkungsgrad=KWT['wirkungsgrad'][i],
                        p_typisch=KWT['p_typisch'][i],
                        spez_info=KWT['spez_info'][i]
                        )
    session.add(kwt)
try:
    session.commit()
except exc.IntegrityError as e:
    print(e)
    session.rollback()

# ################### Kraftwerk #############################
session.query(Kraftwerk).delete()
session.commit()

for i, _ in KW.iterrows():
    kw = Kraftwerk(id=int(KW['id'][i]),
                   bezeichnung=KW['bezeichnung'][i],
                   fk_kraftwerkstyp=int(KW['fk_kraftwerkstyp'][i]),
                   long=KW['long'][i],
                   lat=KW['lat'][i]
                   )
    session.add(kw)
try:
    session.commit()
except exc.IntegrityError as e:
    print(e)
    session.rollback()

# ################### Kraftwerksleistung #############################
session.query(Kraftwerksleistung).delete()
session.commit()

for i, _ in KWL.iterrows():
    kwl = Kraftwerksleistung(id=int(KWL['id'][i]),
                             fk_kraftwerk=int(KWL['fk_kraftwerk'][i]),
                             power_inst=KWL['power_inst'][i],
                             datetime=int(KWL['unix timestamp'][i])
                             )
    session.add(kwl)
try:
    session.commit()
except exc.IntegrityError as e:
    print(e)
    session.rollback()

# ################### VarOpex ######################################
session.query(VarOpex).delete()
session.commit()

for i, _ in OPEX.iterrows():
    var_opex = VarOpex(id=int(OPEX['id'][i]),
                       fk_kraftwerkstyp=int(OPEX['fk_kraftwerkstyp'][i]),
                       datetime=int(OPEX['unix timestamp'][i]),
                       preis=OPEX['preis'][i]
                       )
    session.add(var_opex)
try:
    session.commit()
except exc.IntegrityError as e:
    print(e)
    session.rollback()

# ################### Capex ########################################
session.query(Capex).delete()
session.commit()

for i, _ in CAPEX.iterrows():
    capex = Capex(id=int(CAPEX['id'][i]),
                  fk_kraftwerkstyp=int(CAPEX['fk_kraftwerkstyp'][i]),
                  datetime=int(CAPEX['unix timestamp'][i]),
                  preis=CAPEX['preis'][i]
                  )
    session.add(capex)
try:
    session.commit()
except exc.IntegrityError as e:
    print(e)
    session.rollback()

# ################### Entsorgungspreis #############################
session.query(Entsorgungspreis).delete()
session.commit()

for i, _ in ENTS.iterrows():
    entp = Entsorgungspreis(id=int(ENTS['id'][i]),
                            fk_kraftwerkstyp=int(ENTS['fk_kraftwerkstyp'][i]),
                            long=ENTS['long'][i],
                            lat=ENTS['lat'][i],
                            datetime=int(ENTS['unix timestamp'][i]),
                            preis=ENTS['preis'][i],)
    session.add(entp)
try:
    session.commit()
except exc.IntegrityError as e:
    print(e)
    session.rollback()

# ################### Co2Preis #############################
session.query(Co2Preis).delete()
session.commit()

for i, _ in CO2.iterrows():
    co2p = Co2Preis(id=int(CO2['id'][i]),
                    datetime=int(CO2['unix timestamp'][i]),
                    preis=CO2['preis'][i]
                    )
    session.add(co2p)
try:
    session.commit()
except exc.IntegrityError as e:
    print(e)
    session.rollback()
