from flask import Blueprint, make_response
from services.user_service import UserService
from api.oauth.google import get_user

users_bp = Blueprint('users', __name__, url_prefix='/users')



@users_bp.route('/sign_in', methods=['GET'])
def sign_in():
    response = get_user()

    if response.status_code != 200:
        return response
    
    user = response.get_json()

    try:
        user = UserService().create_user(
            email=user['email'],
            name=user['name'],
            picture=user['picture']
        )
    except Exception as e:
        user = UserService().get_user(email=user['email'])
        if not user:
            return make_response(f"User creation failed: {e}", 500)
    
    # Create session for user and redirect to home page

    return user, 200