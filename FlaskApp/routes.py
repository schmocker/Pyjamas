from .app import app

from .models import *
from .functions import get_agent
from flask import render_template, request
from flask_security import current_user, login_required
import json
import random


@app.route('/')
def home():
    return render_template("home.html",
                           loggedin=current_user.is_authenticated)

@app.route("/agents", methods=['GET', 'POST'])
@login_required
def agents():
    if request.method == 'POST':
        agentName = request.form['agent_name']

        db.session.add(Agent(name=agentName))
        db.session.commit()
    all_agents = Agent.query.all()
    return render_template("agents.html", agents=all_agents,
                           loggedin=current_user.is_authenticated)

@app.route("/agents/<agent>", methods=['GET', 'POST'])
@login_required
def agentX(agent):
        currentAgent = Agent.query.filter_by(name=agent).first()
        return render_template("agentX.html", agent=currentAgent,
                               loggedin=current_user.is_authenticated)

@app.route('/websimgui', methods=['GET', 'POST'])
def websimgui():
    if request.method == 'GET':
        agent_id = request.form.get('agent_id', None)
        if agent_id == None:
            db_agent = Agent.query.first()
        else:
            db_agent = Agent.query.filter(Agent.id == agent_id).first()
        agent_id = db_agent.id
        return render_template("websimgui.html")
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
            db.session.add(Connection(data['agent'],
                                      data['fk_model_used_from'],
                                      data['port_id_from'],
                                      data['fk_model_used_to'],
                                      data['port_id_to']))
            db.session.commit()
            return json.dumps(True)

@app.route('/websimgui/data', methods=['GET', 'POST'])
def websimgui_data():
    if request.method == 'GET':
        agent_id = request.form.get('agent_id', None)
        if agent_id == None:
            db_agent = Agent.query.first()
        else:
            db_agent = Agent.query.filter(Agent.id == agent_id).first()

        print(db_agent.id)

        return json.dumps(db_agent.dict)
