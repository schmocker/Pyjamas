from .db import *
from flask import render_template, request, send_from_directory, url_for
from flask_security import current_user, login_required
import json
from flask import Markup
import markdown2
from .app import app
import os

@app.route('/')
def home():
    return render_template("home.html",
                           loggedin=current_user.is_authenticated,
                           test_agent=Agent.query.first())

@app.route('/doc')
def doc():
    txt = open('README.md', 'r', encoding="utf8").read()
    mkdwn = markdown2.markdown(txt, extras=['extra', 'fenced-code-blocks'])
    content = Markup(mkdwn)
    return render_template("doc.html", content=content, loggedin=current_user.is_authenticated)


@app.route("/agents", methods=['GET', 'POST'])
#@login_required
def agents():
    if request.method == 'GET':
        agent_id = request.args.get('agent', None)
        if agent_id == None:
            all_agents = Agent.query.order_by(Agent.name).all()
            return render_template("agents.html", agents=all_agents, loggedin=current_user.is_authenticated)
        else:
            currentAgent = Agent.query.filter_by(id=agent_id).first()
            if currentAgent != None:
                return render_template("agentX.html", agent=currentAgent, loggedin=current_user.is_authenticated)
            else:
                return "no valid Agent is chosen"



    elif request.method == 'POST':
        try:
            data = json.loads(request.form['data'])
        except:
            print('! -> No field "data" in POST request')
            return json.dumps(False)


        fnc = request.form['fnc']

        if fnc == 'remove_agent':
            Agent.remove(data['agent'])

            all_agents = Agent.query.all()
            return render_template("agents.html", agents=all_agents, loggedin=current_user.is_authenticated)

        if fnc == 'add_agent':
            Agent.add(data['agent_name'])
            return json.dumps(True)






        #agent = Agent.query.filter_by(name=agentName).first()
        #return render_template("agentX.html", agent=agent, loggedin=current_user.is_authenticated)


#@login_required
@app.route('/websimgui', methods=['GET', 'POST'])
def websimgui_GET():
    try:
        if request.method == 'GET':

            fnc = request.args.get('fnc', None)

            data = json.loads(request.args['data'])

            if fnc == 'get_agent':
                agent_id = request.args.get('agent', None)
                db_agent = Agent.query.filter_by(id=agent_id).first()
                return json.dumps(db_agent.dict)

            if fnc == 'get_model_selection':
                return json.dumps(Model.get_all())

            elif fnc == 'get_model_readme':
                return Model_used.get_readme(data['mu_id'])

            elif fnc == 'get_model_properties_view':
                return Model_used.get_properties_view(data['model'])

            elif fnc == 'get_model_properties':
                return json.dumps(Model_used.get_properties(data['model']))

            elif fnc == 'get_model_results_view':
                return Model_used.get_results_view(data['model'])

        elif request.method == 'POST':
            data = json.loads(request.form['data'])

            if 'agent' in data.keys():
                db_agent = Agent.query.filter_by(id=data['agent']).first()

            if request.form['fnc'] == 'set_model_pos':
                Model_used.set_position(data['model'], data['x'], data['y'])

            elif request.form['fnc'] == 'set_model_size':
                Model_used.set_size(data['model'], data['width'], data['height'])

            elif request.form['fnc'] == 'set_model_property':
                Model_used.set_property(data['model'], data['property'], data['value'])

            elif request.form['fnc'] == 'add_connection':
                Connection.add(data['fk_model_used_from'], data['port_id_from'],
                               data['fk_model_used_to'], data['port_id_to'])

            elif request.form['fnc'] == 'add_model_used':
                Model_used.add(data['name'], data['fk_model'], data['agent'])

            elif request.form['fnc'] == 'remove_connection':
                Connection.remove(data['connection'])

            elif request.form['fnc'] == 'remove_model':
                Model_used.remove(data['model'])

            elif request.form['fnc'] == 'start':
                db_agent.start()

            elif request.form['fnc'] == 'pause':
                db_agent.pause()

            elif request.form['fnc'] == 'stop':
                db_agent.stop()

            elif request.form['fnc'] == 'update':
                print("updateing...")
                Model.update_all()

            if 'agent' in data.keys():
                return json.dumps(db_agent.dict)
            else:
                return json.dumps(True)

    except Exception as e:
        print(e)
        print(f"no valid {request.method} request")
        return json.dumps(False)


@app.route('/model_view')
def model_view():
    mu_id = request.args.get('MU_id')
    view = request.args.get('view')

    p = Model_used.get_path_folders(mu_id)
    return render_template(f"{p['topic']}/{p['model']}/{p['version']}/view_{view}/index.html",
                           MU_id=mu_id,
                           view=view)

@app.route('/model_view_static')
def serve_model_view():
    mu_id = request.args.get('MU_id')
    view = request.args.get('view')
    fn = request.args.get('fn')

    p = Model_used.get_path_folders(mu_id)
    return send_from_directory(f"../Models/{p['topic']}/{p['model']}/{p['version']}/view_{view}", fn)
