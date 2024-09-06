from flask import Flask, request, redirect, url_for
from clients.supabase_client import SupabaseClient
from api.oauth.google import google_oauth_bp
from os import getenv

app = Flask(__name__)
app.secret_key = getenv('FLASK_SESSION_SECRET_KEY')

app.register_blueprint(google_oauth_bp)


@app.route('/')
def hello():
    return redirect(url_for('googleoauth.get_user'), code=302)

@app.route('/user', methods=['POST'])
def create_user():
    name = request.get_json().get('name')
    linkedin_url = request.get_json().get('linkedin_url')
    email = request.get_json().get('email')

    if not name or not linkedin_url or not email:
        return 'Name, LinkedIn URL and Email are required', 400
    
    try:
        user = SupabaseClient().insert_data(table='Users', 
            data={
                "email": email,
                "name": name,
                "linkedin_url": linkedin_url,
            }
        )
    except Exception as e:
        return f'Error: {e}', 500

    return user, 201

if __name__ == '__main__':
    app.run()