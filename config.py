import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = 'hard to guess string'
    BOOTSTRAP_VERSION = '1.3.5'
    JQUERY_VERSION = '2.1.4'
    STOKEN = 'zhengweixing'
    SENCODINGAESKEY = 'HiEEk8cVrM6DxTULYoM2y8uUiuWbTfSe3TIFc2wwJOe'
    SCORPID = 'wx708fe43fe320536a'
    QI_YE_SECRET = 'EFnJMWQvyUVPM3c8sDrGwxInrdT54yD3OZI18RgeO7snUDM3XKRAldoOsc6LuJ1k'
    FU_WU_HAO_SECRET= 'd2b3f88cbecddc44e7dc8ce952e4f940'
    APPID = 'wx0faecd9e04ff8fc8'
    PORT = 5678
    WECHAT_URL = '/wechat'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:ZwX1989101355629@114.215.103.152/rg039ugwo6o4vj8r'
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
