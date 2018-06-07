from .db_models import db
import os
from markdown2 import markdown
from flask import Markup
from core import get_models
import json

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

    @property
    def readme(self):
        path = os.path.join(self.path, 'README.md')
        if os.path.isfile(path):
            with open(path, 'r') as f:
                mkdwn = markdown(f.read(), extras=['extra', 'fenced-code-blocks'])
                return Markup(mkdwn)
        else:
            return "no documentation available"

    @property
    def properties_view(self):
        return "Props from " + self.path

    @property
    def results_view(self):
        return "Results from " + self.path

    @property
    def path(self):
        return os.path.join('Models', self.topic, self.name, self.version)

    @classmethod
    def update_all(cls):
        models = get_models()

        for topic in models:
            for model in models[topic]:
                for version in models[topic][model]:
                    info = json.dumps(models[topic][model][version])
                    db_model = cls.query.filter_by(name=model).filter_by(topic=topic).filter_by(version=version).first()

                    # TODO: add orientation form DB to Info
                    if db_model is None:
                        db.session.add(cls(model, topic, version, info=info))
                    else:
                        db_model.info = info
        db.session.commit()

        # delete deleted models out of db
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