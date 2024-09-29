def get_identity_jwt_cookie_config(jwt: str) -> dict:
    return {
        'key': 'identity_jwt',
        'value': jwt,
        'httponly': True,
        'secure': False,   # set to True in prod
        'samesite': 'lax',
        'domain': None,    # set to actual domain in prod
        'max_age': 60 * 15  # 15 minutes in seconds
    }


def get_user_id_from_jwt(identity_jwt: str) -> str:
    user_id = 'decoded from jwt'
    return user_id


def generate_jwt(user_id: str) -> str:
    return 'valid'    #TODO: generate jwt from refresh_token
