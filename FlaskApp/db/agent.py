from .db_main import db, controller

from .model_used import Model_used
from .connection import Connection

import json

class Agent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    def __init__(self, name):
        self.name = name

    @classmethod
    def remove(cls, id):
        obj = cls.query.filter_by(id=id).first()
        db.session.delete(obj)
        db.session.commit()

    @classmethod
    def add(cls, name):
        agent = cls(name=name)
        db.session.add(agent)
        db.session.commit()

    @classmethod
    def rename(cls, id, name):
        obj = cls.query.filter_by(id=id).first()
        obj.name = name
        db.session.commit()

    @classmethod
    def copy_agent(cls, id, name):
        old_obj = cls.query.filter_by(id=id).first()


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
                port_id_from = old_con.port_id_from.replace("m"+str(old_id_from), "m"+str(new_mu_id_from))
                port_id_to = old_con.port_id_to.replace("m"+str(old_id_to), "m"+str(new_mu_id_to))

                new_con = Connection(fk_model_used_from=new_mu_id_from,
                                     port_id_from=port_id_from,
                                     fk_model_used_to=new_mu_id_to,
                                     port_id_to=port_id_to)
                db.session.add(new_con)
                db.session.commit()

    @classmethod
    def get_agent(cls, id):
        return cls.query.filter_by(id=id).first()

    @classmethod
    def get_all_agents(cls):
        return cls.query.order_by(Agent.name).all()




    @classmethod
    def start_agent(cls, id):
        Agent.query.filter_by(id=id).first().start()

    @classmethod
    def pause_agent(cls, id):
        Agent.query.filter_by(id=id).first().pause()

    @classmethod
    def stop_agent(cls, id):
        Agent.query.filter_by(id=id).first().stop()

    @classmethod
    def kill_agent(cls, id):
        Agent.query.filter_by(id=id).first().kill()

    def start(self):
        if not controller.is_agent_running(self.id):
            self.add_full_agent()
        controller.start_agent(self.id)

    def kill(self):
        print("kill")
        controller.kill_agent(self.id)

    def pause(self):
        controller.pause_agent(self.id)

    def stop(self):
        controller.stop_agent(self.id)

    def set_property(self, mu_id, key, value):
        controller.set_property(self.id, mu_id, key, value)

    def add_full_agent(self):

        agent_id = self.id

        controller.force_add_agent(agent_id, self.name)

        for model in self.dict['model_used']:
            to = model['model']['topic']
            na = model['model']['name']
            ve = model['model']['version']

            model_path = f"{to}.{na}.{ve}.model"
            model_id = model['id']
            model_name = model['name']

            controller.add_model(agent_id, model_path, model_id, model_name)

            if model['properties']:
                props = json.loads(model['properties'])
                for property_name, property_value in props.items():
                    controller.set_property(agent_id, model_id, property_name, property_value)

        for conn in self.dict['connection']:
            output_model_id = conn['fk_model_used_from']
            output_name = conn['port_id_from'].split('_', 1)[-1]
            input_model_id = conn['fk_model_used_to']
            input_name = conn['port_id_to'].split('_', 1)[-1]

            controller.link_models(agent_id, output_model_id, output_name, input_model_id, input_name)

    @classmethod
    def dict_agent(cls, id):
        return Agent.query.filter_by(id=id).first().dict


    @property
    def dict(self):
        agent = dict()
        agent['id'] = self.id
        agent['status'] = controller.get_agent_status(self.id)

        agent['model_used'] = list()
        agent['connection'] = list()
        for db_model_used in self.models_used:
            agent['model_used'].append(db_model_used.dict)
            for db_connection in db_model_used.connections_from:
                agent['connection'].append(db_connection.list)
        return agent
