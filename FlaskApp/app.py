from flask import Flask
from flask_socketio import SocketIO
import jinja2

# instantiate Flask app
app = Flask(__name__)

# add /Model as additional template folder for flask to load custom property and result views
app.jinja_loader = jinja2.ChoiceLoader([ app.jinja_loader,jinja2.FileSystemLoader('Models'),])

# load configs
app.config.from_pyfile('config.py')

# create web socket
socketio = SocketIO(app)

# load routes
from .routes import *
