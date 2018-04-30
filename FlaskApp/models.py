from .app import app
from flask_security import UserMixin, RoleMixin
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore


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


class Agents_Models(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fk_agent = db.Column(db.Integer(), db.ForeignKey('agent.id'))
    model_design_name = db.Column(db.String(80), nullable=False)
    model_name = db.Column(db.String(80), nullable=False)
    state = db.Column(db.String(80), nullable=False)
    settings = db.Column(db.String(80))

    def __init__(self, agent_id, model_design_name, model_name, state, settings):
        self.fk_agent = agent_id
        self.model_design_name = model_design_name
        self.model_name = model_name
        self.state = state
        self.settings = settings

# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

# Create a user to test with
@app.before_first_request
def create_user():
    db.create_all()
    all_users = User.query.all()
    for user in all_users:
        user_datastore.delete_user(user)
    db.session.commit()
    user_datastore.create_user(email='spg@fhnw.ch', password='test123')
    db.session.commit()