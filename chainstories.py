import cyborg
import sys
import settings
from flask import Flask, redirect
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager

app = Flask(__name__)
app.config.from_object(settings)
app.secret_key = settings.SECRET_KEY
db = SQLAlchemy(app)
login_manager = LoginManager(app = app)

cyborg.Cyborg(sys.modules[__name__]).setup(app)

@app.route("/")
def redirect_home():
    return redirect("/home")

