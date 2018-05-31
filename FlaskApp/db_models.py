from .app import app
from flask_security import UserMixin, RoleMixin
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore
import random
import json
from Models import get_models
from core import Controller
from os import environ as env


controller = Controller()

### docker-compose
# db_uri = "mysql+pymysql://" + env.get('DB_USER') + ":" + env.get('DB_PASSWORD') + "@" + env.get('DB_HOST') + "/pyjamas"
# app.config['SQLALCHEMY_DATABASE_URI'] = db_uri


db = SQLAlchemy(app)


roles_users = db.Table('roles_users',
                       db.Column('fk_user', db.Integer, db.ForeignKey('user.id')),
                       db.Column('fk_role', db.Integer, db.ForeignKey('role.id')))


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean)
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,backref=db.backref('users', lazy='dynamic'))


class Agent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    active = db.Column(db.Boolean, nullable=False)

    def __init__(self, name):
        self.name = name
        self.active = False


    def start(self):
        try:

            # controller.add_agent(self) TODO: implement method
            controller.add_agent(self.name)

            boxes = []
            links = []

            boxes.append(("Math.Constant.V1.model", "constant number"))
            boxes.append(("Math.Incrementer.V1.model", "Incrementer"))
            boxes.append(("Math.Add.V1.model", "Adder"))
            boxes.append(("InOutput.ConsolePrint.V1.model", "Printer"))
            # boxes.append(("Control.Sleep.V1.model", "Sleeper"))
            boxes.append(("Control.Storage.V1.model", "Storage"))
            boxes.append(("Scheduler.Regular.V1.model", "cron_job"))

            links.append(("constant number", "const", "Adder", "in1"))
            links.append(("Incrementer", "num", "Adder", "in2"))
            links.append(("Storage", "stored", "Adder", "in3"))
            links.append(("Adder", "sum", "Printer", "to_print"))
            # links.append(("Sleeper", "output", "Printer", "to_print"))
            links.append(("Adder", "sum", "Storage", "to_store"))

            mods = {}

            for box in boxes:
                uuid1 = controller.add_model(self.name, box[0], box[1])
                mods[box[1]] = uuid1

            for link in links:
                controller.link_models(self.name, mods[link[0]], link[1], mods[link[2]], link[3])

            controller.start_agent(self.name)


            # controller.start_agent(self.id)
            self.active = True
        except Exception as e:
            print(e)
            self.active = False

        db.session.commit()




    def pause(self):
        # controller.pause_agent(self.id) TODO: implement method
        pass

    def stop(self):
        # controller.stop_agent(self.id) TODO: implement method
        controller.stop_agent(self.name)

        self.active = False
        db.session.commit()


    @property
    def dict(self):
        agent = dict()
        agent['id'] = self.id
        agent['active'] = self.active

        agent['model_used'] = list()
        agent['connection'] = list()
        for db_model_used in self.models_used:
            agent['model_used'].append(db_model_used.dict)
            for db_connection in db_model_used.connections_from:
                agent['connection'].append(db_connection.list)
        return agent

class Model(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    topic = db.Column(db.String(80), nullable=False)
    version = db.Column(db.String(80), nullable=False)
    info = db.Column(db.Text)

    def __init__(self, name, topic, version, info=None):
        self.name = name
        self.topic = topic
        self.version = version
        self.info = info

    @property
    def dict(self):
        atrs = self.__class__.__table__.columns.keys()
        d = {atr: getattr(self, atr) for atr in atrs}
        d['info'] = json.loads(d['info'])
        return d

    @classmethod
    def update_all(cls):
        models = get_models()

        for topic in models:
            for model in models[topic]:
                for version in models[topic][model]:
                    info = json.dumps(models[topic][model][version]["info"])
                    db_model = cls.query.filter_by(name=model).filter_by(topic=topic).filter_by(version=version).first()
                    if db_model is None:
                        db.session.add(cls(model, topic, version, info=info))
                    else:
                        db_model.info = info
        db.session.commit()

        db_model_ids = list()
        for topic in models:
            for model in models[topic]:
                for version in models[topic][model]:
                    db_model = cls.query.filter_by(name=model).filter_by(topic=topic).filter_by(version=version).first()
                    db_model_ids.append(db_model.id)

        cls.query.filter(cls.id.notin_(db_model_ids)).delete(synchronize_session=False)
        db.session.commit()

    @classmethod
    def get_all(cls):
        d = dict()
        for model in cls.query.all():
            if model.topic not in d.keys():
                d[model.topic] = dict()
            if model.name not in d[model.topic].keys():
                d[model.topic][model.name] = dict()
            d[model.topic][model.name][model.version] = dict()
            d[model.topic][model.name][model.version]['id'] = model.id
            d[model.topic][model.name][model.version]['info'] = json.loads(model.info)

        return d





class Model_used(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fk_model = db.Column(db.Integer, db.ForeignKey('model.id', ondelete="CASCADE"), nullable=False)
    fk_agent = db.Column(db.Integer, db.ForeignKey('agent.id', ondelete="CASCADE"), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    settings = db.Column(db.Text, nullable=False)
    x = db.Column(db.Integer)
    y = db.Column(db.Integer)
    width = db.Column(db.Integer)
    height = db.Column(db.Integer)
    ###
    model = db.relationship("Model", foreign_keys=[fk_model],
                            backref=db.backref("models_used", cascade="all, delete-orphan", lazy=True))
    agent = db.relationship("Agent", foreign_keys=[fk_agent],
                            backref=db.backref("models_used", cascade="all, delete-orphan", lazy=True))

    def __init__(self, name, fk_model, fk_agent):
        self.name = name
        self.fk_model = fk_model
        self.fk_agent = fk_agent
        self.width = 120
        self.height = 60
        self.settings = json.dumps(None)

    @property
    def dict(self):
        atrs = self.__class__.__table__.columns.keys()
        d = {atr: getattr(self, atr) for atr in atrs}

        d['settings'] = json.loads(d['settings'])
        d['model'] = self.model.dict

        return d

class Connection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fk_model_used_from = db.Column(db.Integer, db.ForeignKey('model_used.id', ondelete="CASCADE"), nullable=False)
    port_id_from = db.Column(db.String(80), nullable=False)
    fk_model_used_to = db.Column(db.Integer, db.ForeignKey('model_used.id', ondelete="CASCADE"), nullable=False)
    port_id_to = db.Column(db.String(80), nullable=False)
    ###
    model_used_from = db.relationship("Model_used", foreign_keys=[fk_model_used_from],
                                      backref=db.backref("connections_from", cascade="all, delete-orphan", lazy=True))
    model_used_to = db.relationship("Model_used", foreign_keys=[fk_model_used_to],
                                    backref=db.backref("connections_to", cascade="all, delete-orphan", lazy=True))

    def __init__(self, fk_model_used_from, port_id_from, fk_model_used_to, port_id_to):
        self.fk_model_used_from = fk_model_used_from
        self.port_id_from = port_id_from
        self.fk_model_used_to = fk_model_used_to
        self.port_id_to = port_id_to

    @property
    def list(self):
        atrs = self.__class__.__table__.columns.keys()
        return {atr: getattr(self, atr) for atr in atrs}

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
    user_datastore.create_user(email='pyjamas@fhnw.ch', password='PYJAMAS_FHNW')
    db.session.commit()

#unused
def create_dummy_Data():
    Connection.query.delete()
    db.session.commit()

    Model_used.query.delete()
    db.session.commit()

    Model.update_all()

    Agent.query.delete()
    db.session.commit()


    for i in range(0, 5):
        db.session.add(Agent(name="Agent " + str(i)))
    db.session.commit()



    for i in range(0, 25):
        db.session.add(Model_used(name="Used Model " + str(i),
                                  fk_model=random.choice(Model.query.all()).id,
                                  fk_agent=random.choice(Agent.query.all()).id))
    db.session.commit()

