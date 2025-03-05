from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, Session, mapped_column

from models.users import User, UserCreate, UserUpdate

from .core import Base, NotFoundError


class DBUser(Base):
    __tablename__ = "Users"

    id: Mapped[str] = mapped_column(
        primary_key=True, index=True, default=lambda: str(uuid4())
    )
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    is_guest: Mapped[bool] = mapped_column(nullable=False, default=False)
    name: Mapped[str] = mapped_column(nullable=True)
    picture: Mapped[str] = mapped_column(nullable=True)
    profile_id: Mapped[str] = mapped_column(ForeignKey("Profiles.id"), index=True)


def get_user_by_email(email: str, session: Session) -> User:
    user = session.query(DBUser).filter(DBUser.email == email).first()
    if not user:
        raise NotFoundError(f"User with email {email} not found")
    return User(**user.__dict__)


def create_user(user: UserCreate, session: Session) -> User:
    db_user = DBUser(**user.model_dump(exclude_none=True))
    session.add(db_user)
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    session.refresh(db_user)
    return User(**db_user.__dict__)


def get_user_by_id(user_id: str, session: Session) -> User:
    db_user = session.query(DBUser).filter(DBUser.id == user_id).first()
    if not db_user:
        raise NotFoundError(f"User with id {user_id} not found")
    return User(**db_user.__dict__)


def update_user(user: UserUpdate, session: Session) -> User:
    db_user = session.query(DBUser).filter(DBUser.id == user.id).first()
    if not db_user:
        raise NotFoundError(f"User with id {user.id} not found")
    for key, value in user.model_dump(exclude_none=True).items():
        setattr(db_user, key, value)
    session.commit()
    session.refresh(db_user)
    return User(**db_user.__dict__)


def delete_user(user_id: str, session: Session) -> None:
    db_user = session.query(DBUser).filter(DBUser.id == user_id).first()
    if not db_user:
        raise NotFoundError(f"User with id {user_id} not found")
    session.delete(db_user)
    session.commit()
