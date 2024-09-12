import hashlib
import os
from flask import Flask, redirect, url_for
from settings.settings import *

from api.oauth.google import google_oauth_bp

app = Flask(__name__)
app.secret_key =  hashlib.sha256(os.urandom(1024)).hexdigest()

app.register_blueprint(google_oauth_bp)


@app.route('/')
def index():
    return redirect(url_for('sign_in'))

@app.route('/signin')
def sign_in():
    return redirect(url_for('googleoauth.sign_in'))


if __name__ == '__main__':
    app.run()