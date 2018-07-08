from .db_main import db
import os
from markdown2 import markdown
from flask import Markup
import json
import importlib


class Model(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    topic = db.Column(db.String(80), nullable=False)
    version = db.Column(db.String(80), nullable=False)
    properties = db.Column(db.Text, nullable=False, default="{}")
    inputs = db.Column(db.Text, nullable=False, default="{}")
    outputs = db.Column(db.Text, nullable=False, default="{}")

    def __init__(self, name, topic, version, properties="{}", inputs="{}", outputs="{}"):
        self.name = name
        self.topic = topic
        self.version = version
        self.properties = properties
        self.inputs = inputs
        self.outputs = outputs

    @classmethod
    def dict_all(cls):
        return {obj.id: obj.dict for obj in cls.get_all_models()}

    @property
    def dict(self):
        atrs = self.__class__.__table__.columns.keys()
        d = {atr: getattr(self, atr) for atr in atrs}

        for key in ["inputs", "outputs", "properties"]:
            d[key] = json.loads(d[key])

        d['has_property_view'] = self.has_view('properties')
        d['has_result_view'] = self.has_view('result')
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

    def has_view(self, view):
        file = os.path.join("Models", self.topic, self.name, self.version, "view_"+view, "index.html")
        return os.path.isfile(file)

    @property
    def path(self):
        return os.path.join('Models', self.topic, self.name, self.version)

    @classmethod
    def update_all(cls):
        def add_or_update_model(path, topic, model, version):
            try:
                info = importlib.import_module(f"{path}.{topic}.{model}.{version}.model").Model(1, '').get_info()

                if info:
                    db_model = cls.query.filter_by(name=model).filter_by(topic=topic).filter_by(version=version).first()
                    if db_model is None:
                        db.session.add(cls(name=model, topic=topic, version=version,
                                           properties=json.dumps(info['properties']),
                                           inputs=json.dumps(info['inputs']),
                                           outputs=json.dumps(info['outputs'])))
                    else:
                        db_model.properties = json.dumps(info['properties'])
                        db_model.inputs = json.dumps(info['inputs'])
                        db_model.outputs = json.dumps(info['outputs'])
                        unused_models.remove(db_model)
            except Exception as e:
                print(f" --> Error updating {path}.{topic}.{model}.{version}.model ({e})")

        unused_models = cls.query.all()
        path = 'Models'
        s = os.path.sep
        models = [p[0].split(s)[1:4] for p in os.walk(path) if 'model.py' in p[2] and len(p[0].split(s)) is 4]
        # models = [['topic_1', 'model_1', 'version_1'], ..., ['topic_n', 'model_n', 'version_n']]
        [add_or_update_model(path, model[0], model[1], model[2]) for model in models]
        [cls.query.filter_by(id=model.id).delete() for model in unused_models]
        db.session.commit()

    @classmethod
    def get_model(cls, id):
        return cls.query.filter_by(id=id).first()

    @classmethod
    def get_all_models(cls):
        return cls.query.order_by(cls.version).order_by(cls.name).order_by(cls.topic).all()

    @classmethod
    def get_path_folders(cls, id):
        return cls.get_model(id).path_folders

    @property
    def path_folders(self):
        return {'topic': self.topic, 'model': self.name, 'version': self.version}

'''
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
            d[model.topic][model.name][model.version]['properties'] = json.loads(model.properties)
            d[model.topic][model.name][model.version]['inputs'] = json.loads(model.inputs)
            d[model.topic][model.name][model.version]['outputs'] = json.loads(model.outputs)

        return d
'''



