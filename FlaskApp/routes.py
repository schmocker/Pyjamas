from .app import app

from .models import *
from .functions import get_agent
from flask import render_template, request
import json
import random


@app.route('/')
def home():
    return '<a href="/websimgui">Hier gehts zum GUI</a>'


@app.route('/websimgui', methods=['GET', 'POST'])
def websimgui():
    if request.method == 'GET':
        return render_template("WebSimGui.html")
    elif request.method == 'POST':

        if request.form['fnc'] == 'set_model_pos':
            data = json.loads(request.form['data'])
            model_used = Model_used.query.filter(Model_used.id==data['model']).first()
            model_used.x = data['x']
            model_used.y = data['y']
            db.session.commit()
            return json.dumps(True)

        if request.form['fnc'] == 'set_model_size':
            data = json.loads(request.form['data'])
            model_used = Model_used.query.filter(Model_used.id==data['model']).first()
            model_used.width = data['width']
            model_used.height = data['height']
            db.session.commit()
            return json.dumps(True)

        if request.form['fnc'] == 'add_connection':
            data = json.loads(request.form['data'])
            db.session.add(Connection(fk_agent=data['agent'],
                                      fk_model_used_from=data['model_from'],
                                      port_id_from=data['port_from'],
                                      fk_model_used_to=data['model_to'],
                                      port_id_to=data['port_to']))
            db.session.commit()
            return json.dumps(True)

@app.route('/websimgui/data', methods=['GET', 'POST'])
def websimgui_data():
    if request.method == 'GET':
        return get_agent(Agent.query.first().id)





def get_agent(agent_id):
    agent = dict()
    agent['id'] = agent_id




    input_id = 0
    output_id = 0

    agent['models'] = dict()
    for db_model_used in Model_used.query.filter(Model_used.fk_agent == agent_id).all():

        orientations = ['left', 'right', 'top', 'bottom']

        model = dict()

        model['id'] = db_model_used.id
        model['id_html'] = 'model_' + str(db_model_used.id)
        model['name'] = db_model_used.name
        model['x']= db_model_used.x
        model['y'] = db_model_used.y
        model['width'] = db_model_used.width
        model['height'] = db_model_used.height
        model['settings'] = db_model_used.settings

        db_model = Model.query.filter(Model.id == db_model_used.fk_model).first()

        model_info = json.loads(db_model.info)


        for out_in in ['inputs', 'outputs']:
            dock = dict()
            ports = dict()
            for input_key, input_value in model_info[out_in].items():
                port = dict()
                port['name'] = input_value['name']
                port['id'] = input_key
                port['id_model'] = model['id']
                port['id_html'] = 'port_' + str(model['id']) + '_' + input_key
                ports[input_key] = port
            dock['ports'] = ports
            dock['orientation'] = 'left' if out_in == 'inputs' else 'right'
            model[out_in] = dock

        # agent['models'].append(model)
        agent['models'][db_model_used.id] = model


    connections = dict()
    for db_connection in Connection.query.filter(Connection.fk_agent == agent_id).all():
        connection = dict()
        connection['id'] = db_connection.id
        connection['model_from'] = db_connection.fk_model_used_from
        connection['port_from'] = db_connection.port_id_from
        connection['model_to'] = db_connection.fk_model_used_to
        connection['port_to'] = db_connection.port_id_to
        connections[db_connection.id] = connection

    agent['connections'] = connections

    return json.dumps(agent)