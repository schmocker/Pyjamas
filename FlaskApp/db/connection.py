from .db_main import db

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



    @classmethod
    def add(cls, fk_model_used_from, port_id_from, fk_model_used_to, port_id_to):
        obj = cls(fk_model_used_from=fk_model_used_from,
                  port_id_from=port_id_from,
                  fk_model_used_to=fk_model_used_to,
                  port_id_to=port_id_to)
        db.session.add(obj)
        db.session.commit()

    @classmethod
    def remove(cls, id):
        obj = cls.query.filter_by(id=id).first()
        db.session.delete(obj)
        db.session.commit()