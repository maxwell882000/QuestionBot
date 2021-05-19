import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config:
    """
    Configuration class
    """
    API_TOKEN = os.environ.get('API_TOKEN')
    WEBHOOK_HOST = os.environ.get('WEBHOOK_HOST')
    WEBHOOK_URL_BASE = 'https://%s' % WEBHOOK_HOST
    WEBHOOK_URL_PATH = '/%s' % API_TOKEN
    WEBHOOK_SSL_CERT = '/home/telegrambot/certs/cert.pem'

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'db.sqlite3')
    APSCHEDULER_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'apsdb.sqlite3')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    UPLOAD_FOLDER = os.path.join(basedir, 'data')
