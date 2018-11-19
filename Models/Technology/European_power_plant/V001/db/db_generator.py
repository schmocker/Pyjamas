from Models.Technology.European_power_plant.V001.db.db_declarative import Base, Brennstofftyp, Brennstoffpreis, \
    Kraftwerkstyp, Kraftwerk, Kraftwerksleistung, VarOpex, Capex, Entsorgungspreis, Co2Preis

# imports for database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import exc

# general imports
from dotenv import load_dotenv

# pandas for reading excel files
import pandas as pd

# ------------------------- define paths ----------------------------------
source_file = 'Data.xlsx'
db_path = 'sqlite:///pyjamas_powerplants_final.db'

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


# ------------------------- read excel sheets -----------------------------------
BSP = pd.read_excel(source_file, sheet_name='DB_BSP')  # Brennstoffpreise
BST = pd.read_excel(source_file, sheet_name='DB_BST')  # Brennstofftypen
CO2 = pd.read_excel(source_file, sheet_name='DB_CO2')  # Co2-Preise
ENTS = pd.read_excel(source_file, sheet_name='DB_ENTS')  # Entsorgungspreise
KW = pd.read_excel(source_file, sheet_name='DB_KW_KWL')  # Kraftwerke / Kraftwerksleistungen
KWT = pd.read_excel(source_file, sheet_name='DB_KWT')  # Kraftwerkstypen / CAPEX / OPEX


# ------------------------- fill database ---------------------------------------
# pandas reads integers as Int64, which leads to problems with mysql/sqlalchemy
# therefore integers are converted to Int (id=int(...))

# Brennstofftyp
session.query(Brennstofftyp).delete()
session.commit()

for i, _ in BST.iterrows():
    bst = Brennstofftyp(id=int(BST['id'][i]),
                        bezeichnung=BST['bezeichnung'][i],
                        co2emissFakt=BST['co2emissFakt [kgCO2/J]'][i]
                        )
    session.add(bst)
try:
    session.commit()
except exc.IntegrityError as e:
    print(e)
    session.rollback()

# Brennstoffpreis
session.query(Brennstoffpreis).delete()
session.commit()

for i, _ in BSP.iterrows():
    bsp = Brennstoffpreis(id=int(BSP['id'][i]),
                          fk_brennstofftyp=int(BSP['fk_brennstofftyp'][i]),
                          long=BSP['long'][i],
                          lat=BSP['lat'][i],
                          datetime=int(BSP['unix timestamp'][i]),
                          preis=BSP['preis [EUR/J]'][i]
                          )
    session.add(bsp)
try:
    session.commit()
except exc.IntegrityError as e:
    print(e)
    session.rollback()

# Kraftwerkstyp
session.query(Kraftwerkstyp).delete()
session.commit()

for i, _ in KWT.iterrows():
    kwt = Kraftwerkstyp(id=int(KWT['id'][i]),
                        bezeichnung=KWT['bezeichnung'][i],
                        bezeichnung_subtyp=KWT['bezeichnung_subtyp'][i],
                        fk_brennstofftyp=int(KWT['fk_brennstofftyp'][i]),
                        wirkungsgrad=KWT['wirkungsgrad'][i],
                        p_typisch=KWT['p_typisch [W]'][i],
                        spez_info=KWT['spez_info'][i]
                        )
    session.add(kwt)
try:
    session.commit()
except exc.IntegrityError as e:
    print(e)
    session.rollback()

# Kraftwerk
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

# Kraftwerksleistung
session.query(Kraftwerksleistung).delete()
session.commit()

# concatenate columns
KWL_fk_kw = list(pd.concat([KW['fk_kw_1'], KW['fk_kw_2'], KW['fk_kw_3'], KW['fk_kw_4']]))
KWL_p_inst = list(pd.concat([KW['p_inst_1 [W]'], KW['p_inst_2 [W]'], KW['p_inst_3 [W]'], KW['p_inst_4 [W]']]))
KWL_datetime = list(pd.concat([KW['unix timestamp_1'], KW['unix timestamp_2'],
                              KW['unix timestamp_3'], KW['unix timestamp_4']]))

for i, _ in enumerate(KWL_fk_kw):
    kwl = Kraftwerksleistung(id=i+1,  # i starting at 0, id starting at 1
                             fk_kraftwerk=KWL_fk_kw[i],
                             power_inst=KWL_p_inst[i],
                             datetime=KWL_datetime[i]
                             )
    session.add(kwl)
try:
    session.commit()
except exc.IntegrityError as e:
    print(e)
    session.rollback()

# VarOpex
session.query(VarOpex).delete()
session.commit()

OPEX_fk_KWT = list(pd.concat([KWT['fk_kraftwerkstyp'], KWT['fk_kraftwerkstyp']]))
OPEX_datetime = list(pd.concat([KWT['unix timestamp var opex 1'], KWT['unix timestamp var opex 2']]))
OPEX_varopex = list(pd.concat([KWT['var opex 1 [EUR/J]'], KWT['var opex 2 [EUR/J]']]))

for i, _ in enumerate(OPEX_fk_KWT):
    var_opex = VarOpex(id=i+1,  # i starting at 0, id starting at 1
                       fk_kraftwerkstyp=OPEX_fk_KWT[i],
                       datetime=OPEX_datetime[i],
                       preis=OPEX_varopex[i]
                       )
    session.add(var_opex)
try:
    session.commit()
except exc.IntegrityError as e:
    print(e)
    session.rollback()

# Capex
session.query(Capex).delete()
session.commit()

CAPEX_datetime = list(pd.concat([KWT['unix timestamp 1'], KWT['unix timestamp 2']]))
CAPEX_capex = list(pd.concat([KWT['capex 1 [EUR/W]'], KWT['capex 2 [EUR/W]']]))

for i, _ in enumerate(OPEX_fk_KWT):
    capex = Capex(id=i+1,  # i starting at 0, id starting at 1
                  fk_kraftwerkstyp=OPEX_fk_KWT[i],
                  datetime=CAPEX_datetime[i],
                  preis=CAPEX_capex[i]
                  )
    session.add(capex)
try:
    session.commit()
except exc.IntegrityError as e:
    print(e)
    session.rollback()

# Entsorgungspreis
session.query(Entsorgungspreis).delete()
session.commit()

for i, _ in ENTS.iterrows():
    entp = Entsorgungspreis(id=int(ENTS['id'][i]),
                            fk_kraftwerkstyp=int(ENTS['fk_kraftwerkstyp'][i]),
                            long=ENTS['long'][i],
                            lat=ENTS['lat'][i],
                            datetime=int(ENTS['unix timestamp'][i]),
                            preis=ENTS['preis [EUR/J]'][i],)
    session.add(entp)
try:
    session.commit()
except exc.IntegrityError as e:
    print(e)
    session.rollback()

# Co2Preis
session.query(Co2Preis).delete()
session.commit()

for i, _ in CO2.iterrows():
    co2p = Co2Preis(id=int(CO2['id'][i]),
                    datetime=int(CO2['unix timestamp'][i]),
                    preis=CO2['preis [EUR/kg]'][i]
                    )
    session.add(co2p)
try:
    session.commit()
except exc.IntegrityError as e:
    print(e)
    session.rollback()
