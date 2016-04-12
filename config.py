import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')  or 'YOU NEVER GUESS THE STRING'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SIKA_MAIL_SUBJECT_PREFIX = '[Sika]'
    SIKA_MAIL_SENDER = 'Sika Admin <sika@example.com>' 
    SIKA_ADMIN = os.environ.get('SIKA_ADMIN')
    MAIL_SERVER = 'smtp.163.com'
    MAIL_PORT = 25
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    SIKA_POSTS_PER_PAGE = 10
    SIKA_FOLLOWERS_PER_PAGE = 10    
    SIKA_COMMENTS_PER_PAGE = 20
    SIKA_USERS_PER_PAGE = 20

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlit:///' + os.path.join(basedir, 'data.sqlite')

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'productin': ProductionConfig,
    'default': DevelopmentConfig
}
