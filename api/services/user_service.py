from models.users import UserCreate
from sqlalchemy.orm import Session
from db.users import create_user, get_user_by_email
from .session_service import SessionService


def create_or_get_user(user: UserCreate, session: Session):
    try:
        user = create_user(UserCreate, session)
    except Exception:
        user = get_user_by_email(user.email, session)
    
    session_id = SessionService().create_session(user.id)

    return user, session_id