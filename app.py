import hashlib
import os
from flask import Flask, redirect, url_for
from api.oauth.google import google_oauth_bp
from settings.settings import *

app = Flask(__name__)
app.secret_key =  hashlib.sha256(os.urandom(1024)).hexdigest()

app.register_blueprint(google_oauth_bp)


@app.route('/')
def hello():
    return redirect(url_for('googleoauth.get_user'), code=302)


if __name__ == '__main__':
    app.run()