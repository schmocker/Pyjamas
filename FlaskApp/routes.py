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
        return render_template("WebSimGui.html", agent=get_agent())
    elif request.method == 'POST':
        data = json.loads(request.form['data'])
        model = request.form['model']
        print(model)

        models = data['models']

        return json.dumps(data)

@app.route('/websimgui/data', methods=['GET', 'POST'])
def websimgui_data():
    if request.method == 'GET':
        return get_agent()





def get_agent():
    agent = dict()
    agent['id'] = Agent.query.all()[0].id



    input_id = 0
    output_id = 0

    agent['models'] = dict()
    for db_model_used in Model_used.query.filter(Model_used.fk_agent == agent['id']).all():

        orientations = ['left', 'right', 'top', 'bottom']

        model = dict()

        model['id'] = db_model_used.id
        model['id_html'] = 'model_' + str(db_model_used.id)
        model['name'] = db_model_used.name
        model['x'] = db_model_used.x
        model['y'] = db_model_used.y
        model['width'] = db_model_used.width
        model['height'] = db_model_used.height
        model['settings'] = db_model_used.settings

        db_model = Model.query.filter(Model.id == db_model_used.fk_model).first()

        model_info = json.loads(db_model.info)

        for out_in in ['inputs', 'outputs']:
            dock = dict()
            ports = list()
            for input_key, input_value in model_info[out_in].items():
                port = dict()
                port['name'] = input_value['name']
                port['id'] = input_key
                port['id_model'] = model['id']
                port['id_html'] = 'port_' + str(model['id']) + '_' + input_key
                ports.append(port)
            dock['ports'] = ports
            dock['orientation'] = 'left' if out_in == 'inputs' else 'right'
            model[out_in] = dock

        # agent['models'].append(model)
        agent['models'][db_model_used.id] = model


    agent['connections'] = list()

    return json.dumps(agent)