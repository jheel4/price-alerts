from flask import Flask
from src.models.users.views import user_blueprint
from src.common.database import Database

app = Flask(__name__)

app.register_blueprint(user_blueprint,url_prefix='/users')

app.config.from_object('config')
app.secret_key = "123"


@app.before_first_request
def database_initialize():
    Database.initialize()

