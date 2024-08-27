from flask import Flask, request
from clients.supabase_client import SupabaseClient

app = Flask(__name__)


@app.route('/')
def hello():
    return 'Hello, World!'

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