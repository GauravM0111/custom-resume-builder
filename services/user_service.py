from clients.supabase_client import SupabaseClient


class UserService():
    def create_user(self, user_data: dict, overwrite_user_if_exists=False, get_user_if_exists=False) -> dict:
        user_fields = [
            'email',
            'name',
            'picture'
        ]

        user_data = {k:v for k,v in user_data.items() if k in user_fields}

        try:
            user_table = SupabaseClient().table('Users')
            response = user_table.upsert(user_data) if overwrite_user_if_exists else user_table.insert(user_data)
            user = response.execute().data[0]
        except Exception as e:
            user = self.get_user(user_data['email']) if get_user_if_exists else None
            if user:
                print('returning existing user')
            else:
                print(e)

        return user
    

    def get_user(self, email) -> dict:
        response = SupabaseClient().table('Users').select('*').eq('email', email).execute()

        return response.data[0] if response.data else None