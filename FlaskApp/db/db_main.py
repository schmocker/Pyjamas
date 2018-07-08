from FlaskApp.app import app
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore
from core import Controller


# instantiate Controller from pyjamas core
controller = Controller(logging_path='logs', DEBUG=True)
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

# create db on first startup
@app.before_first_request
def create_all():
    db.create_all()
    Model.update_all()

# delete and recreate the default user
@app.before_first_request
def create_user():
    default_user = User.query.filter_by(email=app.config.get('FLASK_USER_EMAIL')).first()
    if default_user:
        user_datastore.delete_user(default_user)
        db.session.commit()

    user_datastore.create_user(email=app.config.get('FLASK_USER_EMAIL'),
                               password=app.config.get('FLASK_USER_PASSWORD'))
    db.session.commit()
