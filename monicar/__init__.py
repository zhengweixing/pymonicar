from flask import Flask
from flask_bootstrap import Bootstrap
from config import config
from wxflask.wxflask import WXFlask
from flask_login import LoginManager
from flask_nav import Nav
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view ='auth.login'
login_manager.session_protection = 'basic'
bootstrap = Bootstrap()
nav = Nav()
#adm_nav = Nav()
weichat = WXFlask()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    db.init_app(app)
    bootstrap.init_app(app)
    nav.init_app(app)
    #adm_nav.init_app(app)
    login_manager.init_app(app)
    weichat.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .admin import admin as admin_blueprint
    app.register_blueprint(admin_blueprint)

    return app


from . import wxhanders
from . import navbar
