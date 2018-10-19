from FlaskApp.app import app
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore
from core import Controller


# instantiate Controller from pyjamas core
controller = Controller(logging_path='logs', DEBUG=app.config['FLASK_DEBUG'])
print("CONTROLLER CREATED")

# instantiate SQLAlchemy for db usage
db = SQLAlchemy(app)

# import all db-models
from .user_role import User, Role
from .agent import Agent
from .model import Model
from .model_used import Model_used
from .connection import Connection

# set up Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


@app.before_first_request
def first_reuqest():
    print('first start')
    create_user()
    create_all()
    print('first start done')


# create db on first startup
def create_all():
    db.create_all()
    Model.update_all()


# delete and recreate the default user
def create_user():
    default_user = User.query.filter_by(email=app.config.get('FLASK_USER_EMAIL')).first()
    if default_user:
        user_datastore.delete_user(default_user)
        db.session.commit()

    user_datastore.create_user(email=app.config.get('FLASK_USER_EMAIL'),
                               password=app.config.get('FLASK_USER_PASSWORD'))
    db.session.commit()
