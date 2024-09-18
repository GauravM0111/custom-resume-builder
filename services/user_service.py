from clients.supabase_client import SupabaseClient


class UserService():
    def create_user(self, user_data: dict, overwrite_user_if_exists=False) -> dict:
        user_fields = [
            'id',
            'email',
            'name',
            'picture',
            'created_at'
        ]

        user_data = {k:v for k,v in user_data.items() if k in user_fields}

        try:
            user = SupabaseClient().table('Users').insert(user_data).execute().data[0]
        except Exception as e:
            user = self.get_user(user_data['email'])
            
            if not user:
                print(f"error creating user: {e}")
            
            elif overwrite_user_if_exists:
                user = SupabaseClient().table('Users').update(user_data).eq("id", user["id"]).execute().data[0]
        
        return user
    

    def get_user(self, email) -> dict:
        response = SupabaseClient().table('Users').select('*').eq('email', email).execute()

        return response.data[0] if response.data else None