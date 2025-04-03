import requests
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from db.profiles import create_profile, get_profile_by_url, update_profile
from models.profiles import CreateProfile, Profile, UpdateProfile
from settings.settings import PROXYCURL_API_KEY, PROXYCURL_BASE_URL


class ProfileService:
    def create_or_update_profile(self, linkedin_url: str, db: Session) -> Profile:
        profile_data = self._get_linkedin_profile(linkedin_url)
        return self._create_or_update_profile(
            CreateProfile(profile=profile_data, url=linkedin_url), db
        )

    def _get_linkedin_profile(self, linkedin_url: str) -> dict:
        url = f"{PROXYCURL_BASE_URL}/linkedin?url={linkedin_url}"
        headers = {"Authorization": f"Bearer {PROXYCURL_API_KEY}"}
        response = requests.get(url, headers=headers)

        if not response.ok:
            raise HTTPException(status_code=response.status_code, detail=response.text)

        return response.json()

    def _create_or_update_profile(self, profile: CreateProfile, db: Session) -> Profile:
        try:
            profile: Profile = create_profile(profile, db)
        except IntegrityError as e:
            existing_profile: Profile = get_profile_by_url(profile.url, db)
            profile = update_profile(
                UpdateProfile(id=existing_profile.id, profile=profile.profile), db
            )

        return profile
