from .app import app
from .functions import get_agent
from flask import render_template, request
import json


@app.route('/')
def home():
    return '<a href="/websimgui">Hier gehts zum GUI</a>'


@app.route('/websimgui', methods=['GET', 'POST'])
def websimgui():
    if request.method == 'GET':
        return render_template("WebSimGui.html", agent=get_agent())
    elif request.method == 'POST':
        data = json.loads(request.form['data'])
        return json.dumps(data)