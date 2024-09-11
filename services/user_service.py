from clients.supabase_client import SupabaseClient

class UserService():
    def create_user(self, email, name=None, picture=None):
        user_data = {
            'email': email
        }

        if name:
            user_data['name'] = name
        
        if picture:
            user_data['picture'] = picture

        try:
            user = SupabaseClient().table('Users').insert(user_data).execute()
        except Exception as e:
            return f'Error: {e}', 500

        return user, 201
    

    def get_user(self, email):
        response = SupabaseClient().table('Users').select().eq('email', email).execute()

        user = response.data[0] if response.data else None

        return user, 200