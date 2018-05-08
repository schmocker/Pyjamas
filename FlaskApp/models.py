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

    @property
    def dict(self):
        agent = dict()
        agent['id'] = self.id

        agent['models'] = dict()
        for db_model_used in Model_used.query.filter(Model_used.fk_agent == self.id).all():
            agent['models'][db_model_used.id] = db_model_used.dict

        agent['connections'] = dict()
        for db_connection in Connection.query.filter(Connection.fk_agent == self.id).all():
            agent['connections'][db_connection.id] = db_connection.dict
        return agent

class Model(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    info = db.Column(db.Text())

    def __init__(self, name, info=None):
        self.name = name
        self.info = info

class Model_used(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fk_model = db.Column(db.Integer(), db.ForeignKey('model.id', ondelete="CASCADE"))
    fk_agent = db.Column(db.Integer(), db.ForeignKey('agent.id', ondelete="CASCADE"))
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

    @property
    def id_html(self):
        return 'model_' + str(self.id)

    @property
    def dict(self):
        d = dict()
        for attr in ['id','id_html','name','x','y','width','height','settings']:
            d[attr] = getattr(self, attr)

        db_model = Model.query.filter(Model.id == self.fk_model).first()

        model_info = json.loads(db_model.info)

        orientations = ['left', 'right', 'top', 'bottom']

        for out_in in ['inputs', 'outputs']:
            dock = dict()
            ports = dict()

            for input_key, input_value in model_info[out_in].items():
                port = dict()
                port['name'] = input_value['name']
                port['id'] = input_key
                port['id_model'] = d['id']
                port['id_html'] = 'port_' + str(d['id']) + '_' + input_key
                ports[input_key] = port
            dock['ports'] = ports
            dock['orientation'] = 'left' if out_in == 'inputs' else 'right'
            d[out_in] = dock
        return d

class Connection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fk_agent = db.Column(db.Integer(), db.ForeignKey('agent.id', ondelete="CASCADE"))
    fk_model_used_from = db.Column(db.Integer(), db.ForeignKey('model_used.id', ondelete="CASCADE"), nullable=False)
    port_id_from = db.Column(db.String(80), nullable=False)
    fk_model_used_to = db.Column(db.Integer(), db.ForeignKey('model_used.id', ondelete="CASCADE"), nullable=False)
    port_id_to = db.Column(db.String(80), nullable=False)

    def __init__(self, fk_agent, fk_model_used_from, port_id_from, fk_model_used_to, port_id_to):
        self.fk_agent = fk_agent
        self.fk_model_used_from = fk_model_used_from
        self.port_id_from = port_id_from
        self.fk_model_used_to = fk_model_used_to
        self.port_id_to = port_id_to

    @property
    def dict(self):
        d = dict()
        for attr in ['id', 'fk_model_used_from', 'port_id_from', 'fk_model_used_to', 'port_id_to']:
            d[attr] = getattr(self, attr)
        return d

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

# Create a user to test with
#@app.before_first_request
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