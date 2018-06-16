from flask import Flask
from os import environ as env
import jinja2
app = Flask(__name__, instance_relative_config=True) # , template_folder="templates"

app.jinja_loader = jinja2.ChoiceLoader([
    app.jinja_loader,
    jinja2.FileSystemLoader('Models'),
])

try:
    app.config.from_pyfile('config.cfg')
except:
    print('no valid file instance/config')
keys = ['FLASK_HOST',
           'FLASK_PORT',
           'FLASK_DEBUG',
           'DB_USER',
           'DB_PASSWORD',
           'DB_HOST',
           'DB_PORT',
           'DB_DATABASE',
           'SECRET_KEY',
           'SECURITY_PASSWORD_SALT',
           'SECURITY_REGISTERABLE',
           'SECURITY_PASSWORD_HASH',
           'SQLALCHEMY_TRACK_MODIFICATIONS']

for key in keys:
    value = env.get(key)

    if value is not None:
        if key in ['FLASK_DEBUG', 'SECURITY_REGISTERABLE', 'SQLALCHEMY_TRACK_MODIFICATIONS']:
            db_value = True if value == '1' else False
        app.config[key] = value


db_values = [app.config.get(db_key) for db_key in ['DB_USER','DB_PASSWORD','DB_HOST','DB_PORT','DB_DATABASE']]
db_uri = ("mysql+pymysql://{}:{}@{}:{}/{}").format(*db_values)
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
print('\n')


from . import routes

