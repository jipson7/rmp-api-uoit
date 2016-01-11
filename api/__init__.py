import csv
from flask import Flask
from flask.ext.cors import CORS

app = Flask(__name__)
CORS(app)

SUNSHINE = {}
reader = csv.reader(open('sunshine-uoit.csv', newline='\n'), delimiter='|')
for row in reader:
    SUNSHINE[row[0]] = row[1]

app.config['DEBUG'] = True
app.config['SUNSHINE'] = SUNSHINE


from api.views import uoit
app.register_blueprint(uoit.uoit, url_prefix='/uoit')

from api import views
