from uuid import uuid4

from sqlalchemy.orm import Session

from db.users import create_user as create_user_db
from db.users import get_user_by_id as get_user_by_id_db
from db.users import update_user as update_user_db
from models.users import User, UserCreate, UserUpdate


class UserService:
    def user_dict_compact(self, user: User) -> dict:
        return {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "created_at": user.created_at.isoformat(),
            "picture": user.picture,
            "profile_id": user.profile_id,
            "is_guest": user.is_guest,
        }

    def create_guest_user(self, db: Session) -> User:
        user_name = f"guest_{uuid4()}"
        user = UserCreate(name=user_name, email=f"{user_name}@guest.com", is_guest=True)
        return create_user_db(user, db)

    def create_user_from_guest(
        self, guest_id: str, user: UserCreate, db: Session
    ) -> User:
        if user.is_guest:
            raise ValueError("Target user is a guest")

        try:
            guest_user = get_user_by_id_db(guest_id, db)
        except Exception:
            raise ValueError("Guest user not found")

        if not guest_user.is_guest:
            raise ValueError("User is not a guest")

        return update_user_db(UserUpdate(id=guest_id, **user.model_dump()), db)
