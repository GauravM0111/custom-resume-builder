from clients.supabase_client import SupabaseClient

class UserService():
    def create_user(self, name, linkedin_url, email):
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