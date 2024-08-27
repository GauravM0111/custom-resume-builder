from supabase import create_client, Client
from os import getenv

class SupabaseClient():
    def __init__(self) -> None:
        self.client: Client = create_client(
            supabase_url=getenv("SUPABASE_API_URL"),
            supabase_key=getenv("SUPABASE_API_KEY")
        )

    def insert_data(self, table: str, data: dict) -> dict:
        print('Inserting data into Supabase...')
        print(f"{table} - {data}")

        try:
            response = self.client.table(table).insert(data).execute()
        except Exception as e:
            print(f"Error: {e}")
            raise e

        return response.data
