from dotenv import load_dotenv
from os import environ


#
# 1. priority: environment variables (example set in docker-compose)
# 2. priority: variables in file ".env" in (they do not overwrite environment variables)
# 3. priority: values specified as default

load_dotenv()

FLASK_HOST = environ.get("FLASK_HOST", default='0.0.0.0')
FLASK_PORT = environ.get("FLASK_PORT", default=5000)
FLASK_DEBUG = environ.get("FLASK_DEBUG", default=False)
FLASK_DEBUG = True if FLASK_DEBUG in [True, 1, 'True'] else False

FLASK_USER_EMAIL = environ.get("FLASK_USER_EMAIL", default='user@pyjamas.com')
FLASK_USER_PASSWORD = environ.get("FLASK_USER_PASSWORD", default='pyjamas_pwd')

DB_HOST = environ.get("DB_HOST", default='localhost')
DB_PORT = environ.get("DB_PORT", default=3306)
DB_DATABASE = environ.get("DB_DATABASE", default='pyjamas')
DB_USER = environ.get("DB_USER", default='pyjamas_db_user')
DB_PASSWORD = environ.get("DB_PASSWORD", default='PYJAMAS_DB_PWD')
DB_DRIVER = environ.get("DB_DRIVER", default='mysql+pymysql')


SECRET_KEY = environ.get("SECRET_KEY", default='pyjamas_secret')

SECURITY_PASSWORD_SALT = environ.get("SECURITY_PASSWORD_SALT", default='/7fD8Ff84gX6Q5r46k452fcvyxedw')
SECURITY_REGISTERABLE = environ.get("SECURITY_REGISTERABLE", default=False)
SECURITY_REGISTERABLE = True if SECURITY_REGISTERABLE in [True, 1, 'True'] else False
SECURITY_PASSWORD_HASH = environ.get("SECURITY_PASSWORD_HASH", default='bcrypt')

if DB_DRIVER == 'sqlite':
    SQLALCHEMY_DATABASE_URI = f"{DB_DRIVER}:///{DB_DATABASE}"
else:
    SQLALCHEMY_DATABASE_URI = f"{DB_DRIVER}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}"

SQLALCHEMY_TRACK_MODIFICATIONS = environ.get("SQLALCHEMY_TRACK_MODIFICATIONS", default=False)
SQLALCHEMY_TRACK_MODIFICATIONS = True if SQLALCHEMY_TRACK_MODIFICATIONS in [True, 1, 'True'] else False
