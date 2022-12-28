from flask import Flask
from flask_cors import CORS, cross_origin

flask_app = Flask(__name__)
CORS(flask_app, supports_credentials=True)

flask_app.config['CORS_HEADERS'] = 'application/json'
flask_app.config['FLASK_ENV'] = 'development'
flask_app.config['SECRET_KEY'] = 'popov'
