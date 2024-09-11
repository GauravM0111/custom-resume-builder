from supabase import Client
from os import getenv

class SupabaseClient(Client):
    def __init__(self) -> None:
        super().__init__(
            supabase_url=getenv('SUPABASE_API_URL'),
            supabase_key=getenv('SUPABASE_API_KEY')
        )
