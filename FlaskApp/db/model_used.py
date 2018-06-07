from .db_models import db
import json
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
    input_orientation = db.Column(db.String(80))  # top, left, bottom, right
    output_orientation = db.Column(db.String(80))
    ###
    model = db.relationship("Model", foreign_keys=[fk_model],
                            backref=db.backref("models_used",cascade="all, delete-orphan", lazy=True))
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

    @classmethod
    def get_readme(cls, id):
        m = cls.query.filter_by(id=id).first()
        return m.model.readme

    @classmethod
    def get_properties_view(cls, id):
        m = cls.query.filter_by(id=id).first()
        return m.model.properties_view

    @classmethod
    def get_results_view(cls, id):
        m = cls.query.filter_by(id=id).first()
        return m.model.results_view

    @classmethod
    def set_position(cls, id, x, y):
        m = cls.query.filter_by(id=id).first()
        m.x = x
        m.y = y
        db.session.commit()

    @classmethod
    def set_size(cls, id, width, height):
        m = cls.query.filter_by(id=id).first()
        m.width = width
        m.height = height
        db.session.commit()