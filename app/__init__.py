from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_uploads import UploadSet, configure_uploads, \
    IMAGES, patch_request_class
from config import config
import flask_whooshalchemyplus


bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
photos = UploadSet('photos',IMAGES)

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    flask_whooshalchemyplus.init_app(app)
    configure_uploads(app, photos)
    patch_request_class(app)  # set maximum file size, default is 16MB
    # print(app.config['UPLOADED_FILES_DEST'])

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .goods import goods as goods_blueprint
    app.register_blueprint(goods_blueprint, url_prefix='/goods')

    from .ck import ck as ck_blueprint
    app.register_blueprint(ck_blueprint, url_prefix='/ck')
    app.jinja_env.add_extension("chartkick.ext.charts")

    return app
