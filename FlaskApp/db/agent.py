from .db_main import db, controller
import json

class Agent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    active = db.Column(db.Boolean, nullable=False)

    def __init__(self, name):
        self.name = name
        self.active = False

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

        if not self.active: # TODO: if application is started (run.py) and no agents are existing. If 'active' is True in the DB it tries to start a non existing agent (maybe set all 'active' in DB to False when application is starting?)
            self.add_full_agent()

        controller.start_agent(self.id)
        self.active = True

        db.session.commit()

    def kill(self):
        print("kill")
        controller.kill_agent(self.id)
        self.active = False
        db.session.commit()

    def pause(self):
        controller.pause_agent(self.id)

    def stop(self):
        controller.stop_agent(self.id)

        self.active = False
        db.session.commit()

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
