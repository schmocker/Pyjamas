from .app import app
from .models import *
from .functions import get_agent
from flask import render_template, request, send_from_directory
from flask_security import current_user, login_required
import json
import random
from flask import Markup


@app.route('/')
def home():
    return render_template("home.html",
                           loggedin=current_user.is_authenticated,
                           test_agent=Agent.query.first())

@app.route('/doc')
def doc():
    content = Markup(open('README.md', 'r').read())
    return render_template("doc.html", content=content, loggedin=current_user.is_authenticated)


@app.route("/agents", methods=['GET', 'POST'])
@login_required
def agents():
    if request.method == 'GET':
        agent_id = request.args.get('agent_id', None)
        if agent_id == None:
            all_agents = Agent.query.all()
            return render_template("agents.html", agents=all_agents, loggedin=current_user.is_authenticated)
        else:
            currentAgent = Agent.query.filter_by(id=agent_id).first()
            return render_template("agentX.html", agent=currentAgent,  loggedin=current_user.is_authenticated)

    elif request.method == 'POST':
        agentName = request.form['agent_name']
        agent = Agent(name=agentName)
        db.session.add(Agent(name=agentName))
        db.session.commit()
        agent = Agent.query.filter_by(name=agentName).first()
        return render_template("agentX.html", agent=agent, loggedin=current_user.is_authenticated)


#@login_required
@app.route('/websimgui', methods=['GET', 'POST'])
def websimgui():
    if request.method == 'GET':
        agent_id = request.args.get('agent_id', None)
        db_agent = Agent.query.filter_by(id=agent_id).first()
        if db_agent != None:
            return render_template("websimgui.html", agent=db_agent, loggedin=current_user.is_authenticated)
        else:
            return "no valid Agent chosen"
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

        if request.form['fnc'] == 'remove_connection':
            data = json.loads(request.form['data'])
            con = Connection.query.filter_by(id=data['connection']).first()
            db.session.delete(con)
            db.session.commit()
            return json.dumps(True)


@app.route('/websimgui/data', methods=['GET', 'POST'])
def websimgui_data():
    if request.method == 'GET':
        agent_id = request.args.get('agent_id', None)
        db_agent = Agent.query.filter_by(id=agent_id).first()


        if db_agent != None:
            return json.dumps(db_agent.dict)

