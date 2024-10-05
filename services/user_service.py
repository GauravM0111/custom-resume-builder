from uuid import uuid4
from models.users import UserCreate, User
from sqlalchemy.orm import Session
from db.users import create_user, get_user_by_email
from auth.session_service import SessionService


def create_or_get_user(user: UserCreate, session: Session) -> tuple[User, str]:
    try:
        user = create_user(UserCreate, session)
    except Exception:
        user = get_user_by_email(user.email, session)
    
    session_id = SessionService().create_session(user.id)

    return user, session_id


def create_guest_user(session: Session) -> tuple[User, str]:
    user = UserCreate(
        name='Guest User',
        email=f'guest_user_{uuid4()}@guest.com',
        is_guest=True
    )
    user = create_user(user, session)

    session_id = SessionService().create_session(user.id)

    return user, session_id
