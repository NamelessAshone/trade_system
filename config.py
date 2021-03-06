import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.qq.com'    #os.environ.get('MAIL_SERVER')
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = '1057803692@qq.com'    #os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = 'iahtnbbkaarkbcgf'    #os.environ.get('MAIL_PASSWORD')
    MAIL_DEBUG = True
    MAIL_DEFAULT_SENDER = None
    FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
    FLASKY_MAIL_SENDER = 'Flasky Admin <' + MAIL_USERNAME + '>'
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')
    BOOTSTRAP_SERVE_LOCAL = True
    UPLOADED_PHOTOS_URL = 'http://localhost:5000/static/'
    UPLOADED_PHOTOS_DEST = os.path.join(os.path.dirname(__file__),'app','static')
    WORK_PATH = os.path.dirname(__file__)

    # settings of models
    GOOD_MAX_PRICE = 10000
    GOOD_MAX_AMOUNT = 10000
    '''
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
    FLASKY_MAIL_SENDER = 'Flasky Admin <flasky@example.com>'
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')
    '''
    
    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')
    WHOOSH_BASE = SQLALCHEMY_DATABASE_URI


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')
    WHOOSH_BASE = SQLALCHEMY_DATABASE_URI

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')
    WHOOSH_BASE = SQLALCHEMY_DATABASE_URI

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
