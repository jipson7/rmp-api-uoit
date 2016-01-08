from flask import Flask
app = Flask(__name__)

app.config.from_object('api.config')

from api.views import uoit

app.register_blueprint(uoit.uoit, url_prefix='/uoit')

from api import views
