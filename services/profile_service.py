from fastapi import HTTPException
import requests
from settings.settings import PROXYCURL_BASE_URL, PROXYCURL_API_KEY
from models.profiles import CreateProfile, UpdateProfile, Profile
from sqlalchemy.orm import Session
from db.profiles import create_profile, update_profile, get_profile_by_url


class ProfileService:
    def create_profile_from_linkedin_url(self, linkedin_url: str, db: Session) -> Profile:
        profile_data = self._get_linkedin_profile(linkedin_url)
        return self._create_or_update_profile(CreateProfile(profile=profile_data, url=linkedin_url), db)


    def _get_linkedin_profile(self, linkedin_url: str) -> dict:
        url = f'{PROXYCURL_BASE_URL}/linkedin?url={linkedin_url}'
        headers = {
            'Authorization': f'Bearer {PROXYCURL_API_KEY}'
        }
        response = requests.get(url, headers=headers)

        if not response.ok:
            raise HTTPException(status_code=response.status_code, detail=response.text)

        return response.json()


    def _create_or_update_profile(self, profile: CreateProfile, db: Session) -> Profile:
        try:
            profile: Profile = create_profile(profile, db)
        except Exception as e:
            try:
                existin_profile: Profile = get_profile_by_url(profile.url)
                profile = update_profile(UpdateProfile(id=existin_profile.id, profile=profile.profile))
            except Exception as _:
                raise e

        return profile
