import os

from flask import Flask
from jinja2 import FileSystemLoader
from chunithm.views import views
from chunithm.func import init_errors


def start_app():
    app = Flask(__name__)
    app.jinja_loader = FileSystemLoader(os.path.join(app.root_path, 'themes/templates'))
    app.static_folder = os.path.join(app.root_path, 'themes/static')
    app.register_blueprint(views)
    app.config['SECRET_KEY'] = os.urandom(64)
    app.config['USERNAME'] = 'admin'
    app.config['PASSWORD'] = 'd5278e5502686c56f86b6e5c8eacc0820690da1177822df26d286bac257173e1296af399794f7bcb0237feca9c68b9e5d705ae675287f619143049874ca74505'
    init_errors(app)

    return app