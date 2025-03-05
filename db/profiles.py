from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, Session, mapped_column

from models.profiles import CreateProfile, Profile, UpdateProfile

from .core import Base, NotFoundError


class DBProfile(Base):
    __tablename__ = "Profiles"

    id: Mapped[str] = mapped_column(
        primary_key=True, index=True, default=lambda: str(uuid4())
    )
    profile: Mapped[dict] = mapped_column(JSON, nullable=False)
    url: Mapped[str] = mapped_column(nullable=False, unique=True)
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, default=lambda: datetime.now(timezone.utc)
    )


def create_profile(profile: CreateProfile, session: Session) -> Profile:
    db_profile = DBProfile(**profile.model_dump(exclude_none=True))
    session.add(db_profile)
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    session.refresh(db_profile)
    return Profile(**db_profile.__dict__)


def get_profile(profile_id: str, session: Session) -> Profile:
    db_profile = session.query(DBProfile).filter(DBProfile.id == profile_id).first()

    if not db_profile:
        raise NotFoundError(f"Profile with id {profile_id} not found")

    return Profile(**db_profile.__dict__)


def get_profile_by_url(url: str, session: Session) -> Profile:
    db_profile = session.query(DBProfile).filter(DBProfile.url == url).first()

    if not db_profile:
        raise NotFoundError(f"Profile with url {url} not found")

    return Profile(**db_profile.__dict__)


def update_profile(profile: UpdateProfile, session: Session) -> Profile:
    db_profile = session.query(DBProfile).filter(DBProfile.id == profile.id).first()

    if not db_profile:
        raise NotFoundError(f"Profile with id {profile.id} not found")

    db_profile.profile = profile.profile
    db_profile.updated_at = datetime.now(timezone.utc)

    try:
        session.commit()
    except Exception as e:
        session.rollback()
        raise e

    session.refresh(db_profile)
    return Profile(**db_profile.__dict__)
