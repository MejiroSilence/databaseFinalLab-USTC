from app import app

class Config(object):
    SECRET_KEY='1145141919810'

app.config.from_object(Config())