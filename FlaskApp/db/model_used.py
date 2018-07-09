from .db_main import db, controller
import json


class Model_used(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fk_model = db.Column(db.Integer, db.ForeignKey('model.id', ondelete="CASCADE"), nullable=False)
    fk_agent = db.Column(db.Integer, db.ForeignKey('agent.id', ondelete="CASCADE"), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    name_v_position = db.Column(db.String(80), nullable=False, default='top outside')
    name_h_position = db.Column(db.String(80), nullable=False, default='center')
    settings = db.Column(db.Text, nullable=False, default=json.dumps({}))
    x = db.Column(db.Integer, default=50)
    y = db.Column(db.Integer, default=50)
    width = db.Column(db.Integer, default=120)
    height = db.Column(db.Integer, default=60)
    properties = db.Column(db.Text, default=json.dumps({}))
    input_orientation = db.Column(db.String(80), default='left')
    output_orientation = db.Column(db.String(80), default='right')
    ###
    model = db.relationship("Model", foreign_keys=[fk_model],
                            backref=db.backref("models_used",cascade="all, delete-orphan", lazy=True))
    agent = db.relationship("Agent", foreign_keys=[fk_agent],
                            backref=db.backref("models_used", cascade="all, delete-orphan", lazy=True))

    def __init__(self, name, fk_model, fk_agent):
        self.name = name
        self.fk_model = fk_model
        self.fk_agent = fk_agent

    @property
    def dict(self):
        atrs = self.__class__.__table__.columns.keys()
        d = {atr: getattr(self, atr) for atr in atrs}
        d['properties'] = json.loads(d['properties'])
        return d


    @classmethod
    def add(cls, name, model, agent):
        obj = cls(name=name, fk_model=model.id, fk_agent=agent.id)
        props = json.loads(model.properties)
        for key, prop in props.items():
            props[key] = prop['default']
        obj.properties = json.dumps(props)

        db.session.add(obj)
        db.session.commit()
        return obj.id

    # get model by id
    @classmethod
    def get_model_used(cls, id):
        return cls.query.filter_by(id=id).first()

    @classmethod
    def remove_byID(cls, id):
        cls.get_model_used(id).remove()

    def remove(self):
        db.session.delete(self)
        db.session.commit()


    @classmethod
    def get_readme_byID(cls, id):
        return cls.get_model_used(id).model.readme

    @classmethod
    def get_results_byID(cls, id, run):
        obj = cls.get_model_used(id)
        result = controller.get_model_results_newer_than(obj.agent.id, obj.id, run)
        return result

    @classmethod
    def set_property_byID(cls, id, key, value):
        cls.get_model_used(id).set_property(key, value)

    def set_property(self, key, value):
        # send to controller
        controller.set_property(self.agent.id, self.id, key, value)
        # update db
        if self.properties:
            props = json.loads(self.properties)
        else:
            props = dict()
        props[key] = value
        self.properties = json.dumps(props)
        db.session.commit()

    @classmethod
    def set_name(cls, id, name):
        cls.get_model_used(id).name = name
        db.session.commit()

    @classmethod
    def set_name_position(cls, id, axis, position):
        obj = cls.get_model_used(id)
        if axis == 'vertical':
            obj.name_v_position = position
        elif axis == 'horizontal':
            obj.name_h_position = position
        db.session.commit()

    @classmethod
    def set_dock_orientation(cls, id, dock, orientation):
        obj = cls.get_model_used(id)
        if dock == 'input':
            obj.input_orientation = orientation
        elif dock == 'output':
            obj.output_orientation = orientation
        db.session.commit()

    @classmethod
    def set_position(cls, id, x, y):
        obj = cls.get_model_used(id)
        obj.x = x
        obj.y = y
        db.session.commit()

    @classmethod
    def set_size(cls, id, width, height):
        obj = cls.get_model_used(id)
        obj.width = width
        obj.height = height
        db.session.commit()

    @classmethod
    def get_path_folders(cls, id):
        return cls.get_model_used(id).path_folders

    @property
    def path_folders(self):
        return self.model.path_folders
