from datetime import datetime
from sqlalchemy.orm import Session, Mapped, mapped_column
from sqlalchemy import JSON
from .core import NotFoundError, Base
from uuid import uuid4
from models.users import User, UserCreate, UserUpdate


class DBUser(Base):
    __tablename__ = "Users"

    id: Mapped[str] = mapped_column(primary_key=True, index=True, default=str(uuid4()))
    email: Mapped[str] = mapped_column(nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.now())
    is_guest: Mapped[bool] = mapped_column(nullable=False, default=False)
    name: Mapped[str] = mapped_column(nullable=True)
    picture: Mapped[str] = mapped_column(nullable=True)
    profile: Mapped[dict] = mapped_column(JSON, nullable=True)

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


def get_user_profile(user_id: str, session: Session) -> dict:
    db_user = session.query(DBUser).filter(DBUser.id == user_id).first()
    if not db_user:
        raise NotFoundError(f"User with id {user_id} not found")
    return db_user.profile
