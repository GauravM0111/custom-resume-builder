from flask import Flask, redirect, url_for
from settings.settings import *
from services.session_service import login_required

from api.oauth.google import google_oauth_bp

app = Flask(__name__)
app.secret_key = FLASK_SECRET_KEY

app.register_blueprint(google_oauth_bp)


@app.route('/')
@login_required
def index(user_id):
    return f'Hello {user_id}', 200

@app.route('/signin')
def sign_in():
    return redirect(url_for('googleoauth.sign_in'))


if __name__ == '__main__':
    app.run()