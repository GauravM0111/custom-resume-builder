from .secret_manager import get_all_secrets


# Secrets
secrets = get_all_secrets()

GOOGLE_OAUTH_CLIENT_SECRET = secrets['GOOGLE_OAUTH_CLIENT_SECRET']
GOOGLE_OAUTH_CLIENT_ID = secrets['GOOGLE_OAUTH_CLIENT_ID']

PROXYCURL_API_KEY = secrets['PROXYCURL_API_KEY']

OPENAI_API_KEY = secrets['OPENAI_API_KEY']

API_SECRET_KEY = secrets['API_SECRET_KEY']


# Params
BASE_URL = 'http://localhost:8000'

GOOGLE_DISCOVERY_DOCUMENT_URL = 'https://accounts.google.com/.well-known/openid-configuration'

OPENAI_ASSISTANT_ID='asst_fixO3zdAF2VSLVasrSpNMrDt'

PROXYCURL_BASE_URL='https://nubela.co/proxycurl/api/v2'

RESUME_SCHEMA_URL='http://json-schema.org/draft-07/schema#'