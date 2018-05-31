from flask import Flask
from os import environ as env

app = Flask(__name__, template_folder="templates", instance_relative_config=True)


app.config.from_pyfile('config.cfg')
print('\nConfigs were loaded from config file.')
keys = ['FLASK_HOST',
           'FLASK_PORT',
           'FLASK_DEBUG',
           'DB_USER',
           'DB_PASSWORD',
           'DB_HOST',
           'DB_PORT',
           'DB_DATABASE']

for key in keys:
    value = env.get(key)

    if value is not None:
        if key == 'FLASK_DEBUG':
            db_value = True if value == '1' else False
        app.config[key] = value
        print((' -> The config "{}" was overwritten by its environment variable').format(key))

db_values = [app.config.get(db_key) for db_key in ['DB_USER','DB_PASSWORD','DB_HOST','DB_PORT','DB_DATABASE']]
db_uri = ("mysql+pymysql://{}:{}@{}:{}/{}").format(*db_values)
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
print('\n')

from .db_models import *
from . import routes