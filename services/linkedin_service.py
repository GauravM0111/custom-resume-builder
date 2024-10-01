from fastapi import HTTPException
import requests
from settings.settings import PROXYCURL_BASE_URL, PROXYCURL_API_KEY


def get_profile_data(linkedin_url: str) -> dict:
    url = f'{PROXYCURL_BASE_URL}/linkedin?url={linkedin_url}'
    headers = {
        'Authorization': f'Bearer {PROXYCURL_API_KEY}'
    }
    response = requests.get(url, headers=headers)

    if not response.ok:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    return response.json()