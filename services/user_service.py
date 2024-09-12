from clients.supabase_client import SupabaseClient


class UserService():
    def create_user(self, overwrite_user_if_exists=False, get_user_if_exists=False, **kwargs):
        user_data = {
            'email': kwargs['email']
        }

        name = kwargs.get('name')
        picture = kwargs.get('picture')

        if name:
            user_data['name'] = name
        
        if picture:
            user_data['picture'] = picture

        try:
            user_table = SupabaseClient().table('Users')
            response = user_table.upsert(user_data) if overwrite_user_if_exists else user_table.insert(user_data)
            user = response.execute().data[0]
        except Exception:
            user = self.get_user(user_data['email']) if get_user_if_exists else None

        return user
    

    def get_user(self, email):
        response = SupabaseClient().table('Users').select('*').eq('email', email).execute()

        return response.data[0] if response.data else None