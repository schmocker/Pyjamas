from .db_main import db, controller
from .model_used import Model_used
from .connection import Connection
from .model import Model
import json




class Agent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    def __init__(self, name):
        self.name = name

# property methods

    @property
    def dict(self):
        agent = dict()
        agent['id'] = self.id
        agent['status'] = self.status

        agent['models'] = Model.dict_all()
        agent['model_used'] = {mu.id: mu.dict for mu in self.models_used}

        agent['connection'] = dict()
        for mu in self.models_used:
            for con in mu.connections_from:
                agent['connection'][con.id] = con.dict
        return agent

    @property
    def status(self):
        return controller.get_agent_status(self.id)

# end property methods

# controller methods

    # start
    @classmethod
    def start_agent(cls, id):
        Agent.query.filter_by(id=id).first().start()

    def start(self):
        if not controller.is_agent_running(self.id):
            self.add_full_agent()
        controller.start_agent(self.id)

    # pause
    @classmethod
    def pause_agent(cls, id):
        Agent.query.filter_by(id=id).first().pause()

    def pause(self):
        controller.pause_agent(self.id)

    # stop
    @classmethod
    def stop_agent(cls, id):
        Agent.query.filter_by(id=id).first().stop()

    def stop(self):
        controller.stop_agent(self.id)

    # kill
    @classmethod
    def kill_agent(cls, id):
        Agent.query.filter_by(id=id).first().kill()

    def kill(self):
        print("kill")
        controller.kill_agent(self.id)

    # helpers
    def set_property(self, mu_id, key, value):
        controller.set_property(self.id, mu_id, key, value)

    def add_full_agent(self):
        agent_id = self.id
        controller.force_add_agent(agent_id, self.name)

        for mu in self.models_used:
            model_path = f"{mu.model.topic}.{mu.model.name}.{mu.model.version}.model"
            controller.add_model(agent_id, model_path, mu.id, mu.name)
            for property_name, property_value in json.loads(mu.properties).items():
                controller.set_property(agent_id, mu.id, property_name, property_value)

        for mu in self.models_used:
            for conn in mu.connections_from:
                output_model_id = conn.fk_model_used_from
                output_name = conn.port_id_from
                input_model_id = conn.fk_model_used_to
                input_name = conn.port_id_to
                controller.link_models(agent_id, output_model_id, output_name, input_model_id, input_name)

# end controller methods

# UI methods

    # add agent to db
    @classmethod
    def add(cls, name):
        agent = cls(name=name)
        db.session.add(agent)
        db.session.commit()

    # remove agent from db
    @classmethod
    def remove_agent(cls, id):
        cls.get_agent(id).remove()

    def remove(self):
        db.session.delete(self)
        db.session.commit()

    # rename agent in db
    @classmethod
    def rename_agent(cls, id, name):
        cls.get_agent(id).rename(name)

    def rename(self, name):
        self.name = name
        db.session.commit()

    # get agent by id
    @classmethod
    def get_agent(cls, id):
        return cls.query.filter_by(id=id).first()

    # get all agents sorted by name
    @classmethod
    def get_all_agents(cls):
        return cls.query.order_by(Agent.name).all()

    # get the dict property by id
    @classmethod
    def dict_agent(cls, id):
        return cls.get_agent(id).dict

    # copy an agent with all models, connections and properties
    @classmethod
    def copy_agent(cls, id, name):
        old_obj = cls.get_agent(id)
        new_obj = cls(name=name)
        db.session.add(new_obj)
        db.session.commit()

        mu_ids = {}
        for old_mu in old_obj.models_used:
            new_mu = Model_used(old_mu.name, old_mu.model.id, new_obj.id)
            db.session.add(new_mu)
            db.session.commit()
            mu_ids[old_mu.id] = new_mu.id

            new_mu.width = old_mu.width
            new_mu.height = old_mu.height
            new_mu.x = old_mu.x
            new_mu.y = old_mu.y
            new_mu.properties = old_mu.properties
            new_mu.input_orientation = old_mu.input_orientation
            new_mu.output_orientation = old_mu.output_orientation
            new_mu.settings = old_mu.settings

            db.session.commit()

        for old_mu in old_obj.models_used:
            for old_con in old_mu.connections_from:
                # fk_model_used
                old_id_from = old_con.fk_model_used_from
                old_id_to = old_con.fk_model_used_to
                new_mu_id_from = mu_ids[old_id_from]
                new_mu_id_to = mu_ids[old_id_to]

                # port_id
                port_id_from = old_con.port_id_from.replace("m" + str(old_id_from), "m" + str(new_mu_id_from))
                port_id_to = old_con.port_id_to.replace("m" + str(old_id_to), "m" + str(new_mu_id_to))

                new_con = Connection(fk_model_used_from=new_mu_id_from,
                                     port_id_from=port_id_from,
                                     fk_model_used_to=new_mu_id_to,
                                     port_id_to=port_id_to)
                db.session.add(new_con)
                db.session.commit()

# end UI methods
