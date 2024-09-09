from settings.secrets_manager import get_all_secrets

_secrets = get_all_secrets()


########### Secrets
GOOGLE_OAUTH_CLIENT_SECRET = _secrets['GOOGLE_OAUTH_CLIENT_SECRET']
GOOGLE_OAUTH_CLIENT_ID = _secrets['GOOGLE_OAUTH_CLIENT_ID']

PROXYCURL_API_KEY = _secrets['PROXYCURL_API_KEY']

OPENAI_API_KEY = _secrets['OPENAI_API_KEY']


########### Params
OPENAI_ASSISTANT_ID='asst_fixO3zdAF2VSLVasrSpNMrDt'

PROXYCURL_BASE_URL='https://nubela.co/proxycurl/api/v2'

RESUME_SCHEMA_URL='http://json-schema.org/draft-07/schema#'