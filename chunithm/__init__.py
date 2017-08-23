import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

from chunithm.func import init_errors


# appの設定
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)

# データベースの設定
sql_uri = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))+"\\app.db"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///"+sql_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True # これがないとwarningが出る
db = SQLAlchemy(app)

# ログインマネージャーの設定
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

app.config.from_object(__name__)
from chunithm import views
