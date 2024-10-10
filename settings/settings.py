from fastapi.templating import Jinja2Templates
from .secret_manager import get_all_secrets


# Secrets
_secrets = get_all_secrets()

GOOGLE_OAUTH_CLIENT_SECRET = _secrets['GOOGLE_OAUTH_CLIENT_SECRET']
GOOGLE_OAUTH_CLIENT_ID = _secrets['GOOGLE_OAUTH_CLIENT_ID']

PROXYCURL_API_KEY = _secrets['PROXYCURL_API_KEY']

OPENAI_API_KEY = _secrets['OPENAI_API_KEY']
OPENAI_ORGANIZATION_ID = _secrets['OPENAI_ORGANIZATION_ID']

API_SECRET_KEY = _secrets['API_SECRET_KEY']


# Params
BASE_URL = 'http://localhost:8000'
TEMPLATES = Jinja2Templates(directory="templates")

GOOGLE_DISCOVERY_DOCUMENT_URL = 'https://accounts.google.com/.well-known/openid-configuration'

PROXYCURL_BASE_URL='https://nubela.co/proxycurl/api/v2'

RESUME_SCHEMA_URL='https://raw.githubusercontent.com/jsonresume/resume-schema/v1.0.0/schema.json'
EXAMPLE_RESUME_URL='https://raw.githubusercontent.com/jsonresume/resume-schema/v1.0.0/sample.resume.json'

UNAUTHENTICATED_ENDPOINTS = [
    "/signin",
    "/googleoauth",
    "/googleoauth/callback",
]
