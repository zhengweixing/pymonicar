import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = 'hard to guess string'
    BOOTSTRAP_VERSION = '1.3.5'
    JQUERY_VERSION = '2.1.4'
    STOKEN = 'zhengweixing'
    SENCODINGAESKEY = 'xxxxxxxxxxxxx'
    SCORPID = 'wx708fe43fe320536a'
    QI_YE_SECRET = 'xxxxxxxxxxxxxxxxxxxxxxxxxx'
    FU_WU_HAO_SECRET= 'd2b3f88cbecddc44e7dc8ce952e4f940'
    APPID = 'wx0faecd9e04ff8fc8'
    PORT = 5678
    WECHAT_URL = '/wechat'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:xxxxxxxxxxxxx@127.0.0.1/rg039ugwo6o4vj8r'
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True


class ProductionConfig(Config):

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)


class UnixConfig(ProductionConfig):
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        # log to syslog
        import logging
        from logging.handlers import SysLogHandler
        syslog_handler = SysLogHandler()
        syslog_handler.setLevel(logging.WARNING)
        app.logger.addHandler(syslog_handler)


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'unix': UnixConfig,

    'default': DevelopmentConfig
}
