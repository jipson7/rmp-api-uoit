from flask import Flask
from flask.ext.cors import CORS

app = Flask(__name__)
CORS(app)
app.config.from_object('api.config')

from api.views import uoit
app.register_blueprint(uoit.uoit, url_prefix='/uoit')

from api import views
