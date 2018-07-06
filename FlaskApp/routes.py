from .db import *
from flask import render_template, request, send_from_directory, url_for, redirect
from flask_security import current_user, login_required
import json
from flask import Markup
import markdown2
from .app import app


@app.route('/')
def home():
    txt = open('README.md', 'r', encoding="utf8").read()
    mkdwn = markdown2.markdown(txt, extras=['extra', 'fenced-code-blocks'])
    return render_template("home.html", content=Markup(mkdwn), loggedin=current_user.is_authenticated)


# @login_required
@app.route("/agents", methods=['GET', 'POST'])
def agents():
    if request.method == 'GET':
        agent_id = request.args.get('agent', None, int)
        agent = Agent.get_agent(agent_id)
        if agent:
            return render_template("agentX.html", agent=agent, loggedin=current_user.is_authenticated)
        else:
            return render_template("agents.html", agents=Agent.get_all_agents(), loggedin=current_user.is_authenticated)

    elif request.method == 'POST':
        fnc = request.form['fnc']

        if fnc == 'remove_agent':
            agent_id = request.form.get('agent_id', None, int)
            Agent.remove(agent_id)
            return redirect(url_for('.agents'))

        elif fnc == 'add_agent':
            name = request.form.get('agent_name', None, str)
            Agent.add(name)
            return redirect(url_for('.agents'))

        elif fnc == 'rename_agent':
            id = request.form.get('agent_id', None, int)
            name = request.form.get('agent_name', None, str)
            Agent.rename(id, name)
            return redirect(url_for('.agents'))

        elif fnc == 'copy_agent':
            id = request.form.get('agent_id', None, int)
            name = request.form.get('agent_name', None, str)
            Agent.copy_agent(id, name)
            return redirect(url_for('.agents'))


# @login_required
@app.route('/websimgui', methods=['GET', 'POST'])
def web_sim_gui():
    try:

        if request.method == 'GET':
            fnc = request.args.get('fnc', None, str)
            data = request.args.get('data', None, str)
            data = json.loads(data) if data else data

            if fnc == 'get_agent':
                agent_id = request.args.get('agent', None)
                db_agent = Agent.get_agent(agent_id)
                return json.dumps(db_agent.dict)

            if fnc == 'get_model_selection':
                return json.dumps(Model.get_all())

            elif fnc == 'get_model_readme':
                return Model_used.get_readme(data['mu_id'])

            elif fnc == 'get_model_properties':
                return json.dumps(Model_used.get_properties(data['model']))

            elif fnc == 'get_mu_results':
                results = Model_used.get_results(data['mu_id'], data['mu_run'])
                filter = data.get('filter')

                '''
                Filter results
                --------------
                Example: {'h': ['output1', 'height'], 't': [output2, 'times', 0]}
                this will search for:
                - result['output1']['height'] and stores it in result['h']
                - result['output1']['times'][0] and stores it in result['t']
                all other data will no be returned
                '''
                if filter and results:
                    filtered_results = {}
                    for k, v in filter.items():
                        filtered_results[k] = results['result']
                        for f in v:
                            filtered_results[k] = filtered_results[k][f]
                    results['result'] = filtered_results

                results = json.dumps(results)
                return results

        elif request.method == 'POST':
            fnc = request.form.get('fnc', None, str)
            data = request.form.get('data', None, str)
            data = json.loads(data) if data else data
            request_return = None;

            if fnc == 'set_model_pos':
                Model_used.set_position(data['model'], data['x'], data['y'])

            elif fnc == 'set_model_size':
                Model_used.set_size(data['model'], data['width'], data['height'])

            elif fnc == 'set_model_property':
                Model_used.set_property(data['model'], data['property'], data['value'])

            elif fnc == 'set_model_name':
                Model_used.set_name(data['mu_id'], data['name'])

            elif fnc == 'set_model_name_position':
                Model_used.set_name_position(data['mu_id'], data['axis'], data['position'])


            elif fnc == 'set_model_dock_orientation':
                Model_used.set_dock_orientation(data['mu_id'], data['dock'], data['orientation'])

            elif fnc == 'add_connection':
                Connection.add(data['fk_model_used_from'], data['port_id_from'],
                               data['fk_model_used_to'], data['port_id_to'])

            elif fnc == 'add_model_used':
                id = Model_used.add(data['name'], data['fk_model'], data['agent'])
                request_return = id

            elif fnc == 'remove_connection':
                Connection.remove(data['connection'])

            elif fnc == 'remove_model':
                Model_used.remove(data['model'])

            elif fnc == 'start':
                Agent.start_agent(data['agent'])

            elif fnc == 'pause':
                Agent.pause_agent(data['agent'])

            elif fnc == 'stop':
                Agent.stop_agent(data['agent'])

            elif fnc == 'kill':
                Agent.kill_agent(data['agent'])

            elif fnc == 'update':
                Model.update_all()

            else:
                fnc = 'None' if fnc is None else fnc
                raise ValueError(f"Function '{fnc}' is not defined for websimgui")

            if 'agent' in data.keys():
                data = Agent.dict_agent(data['agent'])
                data['request_return'] = request_return
                return json.dumps(data)
            else:
                return json.dumps(True)

    except Exception as e:
        print(f"no valid {request.method} request ({e})")
        return json.dumps(False)


# @login_required
@app.route('/model_view')
def model_view():
    mu_id = request.args.get('MU_id', None, int)
    view = request.args.get('view', None, str)

    p = Model_used.get_path_folders(mu_id)
    return render_template(f"{p['topic']}/{p['model']}/{p['version']}/view_{view}/index.html", MU_id=mu_id, view=view)


# @login_required
@app.route('/model_view_static')
def serve_model_view():
    mu_id = request.args.get('MU_id', None, int)
    view = request.args.get('view', None, str)
    fn = request.args.get('fn', None, str)

    p = Model_used.get_path_folders(mu_id)
    return send_from_directory(f"../Models/{p['topic']}/{p['model']}/{p['version']}/view_{view}", fn)
