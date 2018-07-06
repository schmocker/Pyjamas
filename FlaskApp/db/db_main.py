from FlaskApp.app import app
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore
from core import Controller


controller = Controller(logging_path='logs', DEBUG=True)
print("CONTROLLER CREATED") #TODO: Multiple empty controllers get created (1 every time a agent is startet -> see log files) @Tobias do you know why?
db = SQLAlchemy(app)


from .user_role import User, Role
from .agent import Agent
from .model import Model
from .model_used import Model_used
from .connection import Connection



# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


@app.before_first_request
def create_all():
    db.create_all()
    Model.update_all()

# Create a default user
@app.before_first_request
def create_user():
    default_user = User.query.filter_by(email=app.config.get('FLASK_USER_EMAIL')).first()
    user_datastore.delete_user(default_user)
    db.session.commit()

    user_datastore.create_user(email=app.config.get('FLASK_USER_EMAIL'),
                               password=app.config.get('FLASK_USER_PASSWORD'))
    db.session.commit()
