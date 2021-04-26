from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

# FLask related stuffs
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dqm.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECRET_KEY'] = 'c8dc3e2733290e4e9ea153a5'
db = SQLAlchemy(app)
bcryt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login_page'
login_manager.login_message_category = 'info'

with app.app_context():
    from dqm import routes
    from .plotlydash.dashboard import init_dashboard
    app = init_dashboard(app)



