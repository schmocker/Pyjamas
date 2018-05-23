from .app import app
from .db_models import *
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
            all_agents = Agent.query.order_by(Agent.name).all()
            return render_template("agents.html", agents=all_agents, loggedin=current_user.is_authenticated)
        else:
            currentAgent = Agent.query.filter_by(id=agent_id).first()
            return render_template("agentX.html", agent=currentAgent,  loggedin=current_user.is_authenticated)

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
            db.session.add(Agent(name=data['agent_name']))
            db.session.commit()
            return json.dumps(True)




        #agent = Agent.query.filter_by(name=agentName).first()
        #return render_template("agentX.html", agent=agent, loggedin=current_user.is_authenticated)


#@login_required
@app.route('/websimgui', methods=['GET', 'POST'])
def websimgui():


    if request.method == 'GET':
        fnc = request.args.get('fnc', None)

        if fnc == 'get_model_selection':
            return json.dumps(Model.get_all())

        else:
            agent_id = request.args.get('agent_id', None)
            db_agent = Agent.query.filter_by(id=agent_id).first()
            if db_agent != None:
                return render_template("websimgui.html", agent=db_agent, loggedin=current_user.is_authenticated)
            else:
                return "no valid Agent chosen"

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
            model_used = Model_used.query.filter(Model_used.id==data['model']).first()
            model_used.x = data['x']
            model_used.y = data['y']
            db.session.commit()

        if request.form['fnc'] == 'set_model_size':
            model_used = Model_used.query.filter(Model_used.id==data['model']).first()
            model_used.width = data['width']
            model_used.height = data['height']
            db.session.commit()

        if request.form['fnc'] == 'add_connection':
            db.session.add(Connection(data['fk_model_used_from'],
                                      data['port_id_from'],
                                      data['fk_model_used_to'],
                                      data['port_id_to']))
            db.session.commit()

        if request.form['fnc'] == 'add_model_used':
            db.session.add(Model_used(data['name'],
                                      data['fk_model'],
                                      data['agent']))
            db.session.commit()

        if request.form['fnc'] == 'remove_connection':
            con = Connection.query.filter_by(id=data['connection']).first()
            db.session.delete(con)
            db.session.commit()

        if request.form['fnc'] == 'remove_model':
            model_used = Model_used.query.filter_by(id=data['model']).first()
            db.session.delete(model_used)
            db.session.commit()

        if request.form['fnc'] == 'start':
            db_agent.start()

        if request.form['fnc'] == 'pause':
            db_agent.pause()

        if request.form['fnc'] == 'stop':
            db_agent.stop()

        if request.form['fnc'] == 'update':
            print("updateing...")

        return json.dumps(db_agent.dict)






@app.route('/websimgui/data', methods=['GET', 'POST'])
def websimgui_data():
    if request.method == 'GET':
        agent_id = request.args.get('agent_id', None)
        db_agent = Agent.query.filter_by(id=agent_id).first()


        if db_agent != None:
            return json.dumps(db_agent.dict)

        else:
            return json.dumps(False)


@app.route('/test')
def test():
    return render_template("test.html")

@app.route('/model')
def model():
    used_model_id = Model_used.query.first().id # Todo: ersetzten mit id von request

    used_model = Model_used.query.filter_by(id=used_model_id).first()

    return "Model"
