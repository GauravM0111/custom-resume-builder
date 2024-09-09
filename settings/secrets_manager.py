from clients.supabase_client import SupabaseClient


def get_all_secrets():
    supabase = SupabaseClient().client

    try:
        # Query the vault.decrypted_secrets table
        response = supabase.schema('vault').table('decrypted_secrets').select('*').execute()
    except Exception as e:
        print(f"Error loading secrets: {e}")
        raise e
    
    secrets = {}

    for secret in response.data:
        secrets[secret['name']] = secret['decrypted_secret']

    return secrets