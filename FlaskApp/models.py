from .app import app
from flask_security import UserMixin, RoleMixin
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore
import random
import json

db = SQLAlchemy(app)

roles_users = db.Table('roles_users',
                       db.Column('fk_user', db.Integer(), db.ForeignKey('user.id')),
                       db.Column('fk_role', db.Integer(), db.ForeignKey('role.id')))


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,backref=db.backref('users', lazy='dynamic'))


class Agent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Agent %r>' % self.name

class Model(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    info = db.Column(db.Text())

    def __init__(self, name, info=None):
        self.name = name
        self.info = info

class Model_used(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fk_model = db.Column(db.Integer(), db.ForeignKey('model.id'))
    fk_agent = db.Column(db.Integer(), db.ForeignKey('agent.id'))
    name = db.Column(db.String(80), nullable=False)
    settings = db.Column(db.String(80))
    x = db.Column(db.Integer())
    y = db.Column(db.Integer())
    width = db.Column(db.Integer())
    height = db.Column(db.Integer())

    def __init__(self, name, fk_model, fk_agent):
        self.name = name
        self.fk_model = fk_model
        self.fk_agent = fk_agent
        self.width = 120
        self.height = 60

class Connection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fk_agent = db.Column(db.Integer(), db.ForeignKey('agent.id'))
    fk_model_used_from = db.Column(db.Integer(), db.ForeignKey('model_used.id'), nullable=False)
    port_id_from = db.Column(db.String(80), nullable=False)
    fk_model_used_to = db.Column(db.Integer(), db.ForeignKey('model_used.id'), nullable=False)
    port_id_to = db.Column(db.String(80), nullable=False)

    def __init__(self, fk_agent, fk_model_used_from, port_id_from, fk_model_used_to, port_id_to):
        self.fk_agent = fk_agent
        self.fk_model_used_from = fk_model_used_from
        self.port_id_from = port_id_from
        self.fk_model_used_to = fk_model_used_to
        self.port_id_to = port_id_to

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

# Create a user to test with
@app.before_first_request
def create_user():
    db.create_all()

    for user in User.query.all():
        user_datastore.delete_user(user)
    db.session.commit()
    user_datastore.create_user(email='spg@fhnw.ch', password='test123')
    db.session.commit()

    # Create new Dummy Data !! deletes existing Data
    if True:
        Connection.query.delete()
        db.session.commit()

        Model_used.query.delete()
        db.session.commit()

        Model.query.delete()
        db.session.commit()

        Agent.query.delete()
        db.session.commit()


        for i in range(0, 5):
            db.session.add(Agent(name="Agent " + str(i)))
        db.session.commit()

        for i in range(0, 5):
            inputs = list()
            db.session.add(Model(name="Model " + str(i),
                                 info=get_model_infos()))
        db.session.commit()

        for i in range(0, 25):
            db.session.add(Model_used(name="Used Model " + str(i),
                                      fk_model=random.choice(Model.query.all()).id,
                                      fk_agent=random.choice(Agent.query.all()).id))
        db.session.commit()

def get_model_infos():
    inputs = {'input_1': {'name': 'Input 1'},
              'input_2': {'name': 'Input 2'},
              'input_3': {'name': 'Input 3'}}
    outputs = {'output_1': {'name': 'Output 1'},
               'output_2': {'name': 'Output 2'}}
    info = {'inputs': inputs, 'outputs': outputs}

    return json.dumps(info)