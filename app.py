import hashlib
import os
from flask import Flask, redirect, url_for
from settings.settings import *

from api.oauth.google import google_oauth_bp
from api.users import users_bp

app = Flask(__name__)
app.secret_key =  hashlib.sha256(os.urandom(1024)).hexdigest()

app.register_blueprint(google_oauth_bp)
app.register_blueprint(users_bp)


@app.route('/')
def hello():
    return redirect(url_for('users.sign_in'), code=302)


if __name__ == '__main__':
    app.run()