from .db_main import db
import os
from markdown2 import markdown
from flask import Markup
from core import get_model_info
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
        d['has_property_view'] = self.has_property_view
        d['has_result_view'] = self.has_result_view
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
    def has_property_view(self):
        file = os.path.join("Models", self.topic, self.name, self.version, "view_properties", "index.html")
        return os.path.isfile(file)

    @property
    def has_result_view(self):
        file = os.path.join("Models", self.topic, self.name, self.version, "view_result", "index.html")
        return os.path.isfile(file)

    @property
    def path(self):
        return os.path.join('Models', self.topic, self.name, self.version)

    @classmethod
    def update_all(cls):
        def add_or_update_model(topic, model, version):
            info = get_model_info(path, topic, model, version)
            if info:
                info = json.dumps(info)
                db_model = cls.query.filter_by(name=model).filter_by(topic=topic).filter_by(version=version).first()
                if db_model is None:
                    db.session.add(cls(name=model, topic=topic, version=version, info=info))
                else:
                    db_model.info = info
                    unused_models.remove(db_model)

        unused_models = cls.query.all()
        path = 'Models'
        s = os.path.sep
        models = [p[0].split(s)[1:4] for p in os.walk(path) if 'model.py' in p[2] and len(p[0].split(s)) is 4]
        # models = [['topic_1', 'model_1', 'version_1'], ..., ['topic_n', 'model_n', 'version_n']]
        [add_or_update_model(model[0], model[1], model[2]) for model in models]
        [cls.query.filter_by(id=model.id).delete() for model in unused_models]
        db.session.commit()

    @classmethod
    def get_model(cls, id):
        return cls.query.filter_by(id=id).first()

    @classmethod
    def get_all_models(cls):
        return cls.query.order_by(Model.topic).all()

    @classmethod
    def get_all(cls):
        d = dict()
        for model in cls.get_all_models():
            if model.topic not in d.keys():
                d[model.topic] = dict()
            if model.name not in d[model.topic].keys():
                d[model.topic][model.name] = dict()
            d[model.topic][model.name][model.version] = dict()
            d[model.topic][model.name][model.version]['id'] = model.id
            d[model.topic][model.name][model.version]['info'] = json.loads(model.info)

        return d

    @classmethod
    def get_path_folders(cls, id):
        return cls.query.filter_by(id=id).first().path_folders

    @property
    def path_folders(self):
        return {'topic': self.topic,
                'model': self.name,
                'version': self.version}

