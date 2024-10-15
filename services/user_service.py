from uuid import uuid4
from models.users import UserCreate, User, UserUpdate
from sqlalchemy.orm import Session
from db.users import (
    create_user as create_user_db,
    get_user_by_email as get_user_by_email_db,
    get_user_by_id as get_user_by_id_db,
    update_user as update_user_db
)
from auth.session_service import SessionService


class UserService:
    def create_user(self, user: UserCreate, db: Session, create_session: bool = True) -> tuple[User, str]:
        user = create_user_db(user, db)
        session_id = SessionService().create_session(user.id) if create_session else None

        return user, session_id


    def get_user_by_email(self, email: str, db: Session, create_session: bool = True) -> tuple[User, str]:
        user = get_user_by_email_db(email, db)
        session_id = SessionService().create_session(user.id) if create_session else None

        return user, session_id


    def create_guest_user(self, db: Session, create_session: bool = True) -> tuple[User, str]:
        user_name = f'guest_{uuid4()}'
        user = UserCreate(
            name=user_name,
            email=f'{user_name}@guest.com',
            is_guest=True
        )
        return self.create_user(user, db, create_session)


    def create_user_from_guest(self, guest_id: str, user: UserCreate, db: Session) -> User:
        try:
            guest_user = get_user_by_id_db(guest_id, db)
        except Exception:
            raise ValueError('Guest user not found')
        
        if not guest_user.is_guest:
            raise ValueError('User is not a guest')
        
        return update_user_db(UserUpdate(id=guest_id, is_guest=False, **user.model_dump()), db)
