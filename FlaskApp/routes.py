from .app import app
from .db_models import *
from .functions import get_agent
from flask import render_template, request, send_from_directory
from flask_security import current_user, login_required
import json
import random
from flask import Markup
import  markdown2
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
            db_agent = Agent.query.filter_by(id=data['agent']).first()
            db.session.delete(db_agent)
            db.session.commit()

            all_agents = Agent.query.all()
            return render_template("agents.html", agents=all_agents, loggedin=current_user.is_authenticated)

        if fnc == 'add_agent':
            db.session.add(Agent(name=data['agent_name'])) # TODO: give agent PK as id
            db.session.commit()
            return json.dumps(True)






        #agent = Agent.query.filter_by(name=agentName).first()
        #return render_template("agentX.html", agent=agent, loggedin=current_user.is_authenticated)


#@login_required
@app.route('/websimgui', methods=['GET', 'POST'])
def websimgui():


    if request.method == 'GET':
        fnc = request.args.get('fnc', None)
        data = json.loads(request.args['data'])

        if fnc == 'get_model_selection':
            return json.dumps(Model.get_all())

        elif fnc == 'get_model_description':
            db_model_used = Model_used.query.filter_by(id=data['model']).first()
            model_info = json.loads(db_model_used.model.info)
            return model_info['description']

        elif fnc == 'get_model_view':
            ## Todo: @Simon get view from model
            return "model view from routes.py"

        else:
            return "no valid get request"

    elif request.method == 'POST':

        try:
            data = json.loads(request.form['data'])
        except:
            print('! -> No field "data" in POST request')
            return json.dumps(False)



        print('Agent ' + str(data['agent']) + ' (POST): ' + request.form['fnc'])

        db_agent = Agent.query.filter_by(id=data['agent']).first()

        if db_agent == None:
            return json.dumps(False)

        if request.form['fnc'] == 'set_model_pos':
            Model_used.set_position(data['model'], data['x'], data['y'])

        elif request.form['fnc'] == 'set_model_size':
            Model_used.set_size(data['model'], data['width'], data['height'])

        elif request.form['fnc'] == 'add_connection':
            db.session.add(Connection(data['fk_model_used_from'],
                                      data['port_id_from'],
                                      data['fk_model_used_to'],
                                      data['port_id_to']))
            db.session.commit()

        elif request.form['fnc'] == 'add_model_used':
            db.session.add(Model_used(data['name'],
                                      data['fk_model'],
                                      data['agent']))
            db.session.commit()

        elif request.form['fnc'] == 'remove_connection':
            con = Connection.query.filter_by(id=data['connection']).first()
            db.session.delete(con)
            db.session.commit()

        elif request.form['fnc'] == 'remove_model':
            model_used = Model_used.query.filter_by(id=data['model']).first()
            db.session.delete(model_used)
            db.session.commit()

        elif request.form['fnc'] == 'start':
            db_agent.start()

        elif request.form['fnc'] == 'pause':
            db_agent.pause()

        elif request.form['fnc'] == 'stop':
            db_agent.stop()

        elif request.form['fnc'] == 'update':
            print("updateing...")
            Model.update_all()

        return json.dumps(db_agent.dict)






@app.route('/websimgui/data', methods=['GET', 'POST'])
def websimgui_data():
    if request.method == 'GET':
        agent_id = request.args.get('agent', None)
        db_agent = Agent.query.filter_by(id=agent_id).first()


        if db_agent != None:
            return json.dumps(db_agent.dict)

        else:
            return json.dumps(False)


@app.route('/test')
def test():
    return render_template("../Models/Technology/European_power_plant/V001/view/test.html")


