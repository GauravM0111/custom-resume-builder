from uuid import uuid4
from sqlalchemy.orm import Session, Mapped, mapped_column
from sqlalchemy import JSON, ForeignKey
from datetime import datetime
from models.resumes import Resume, CreateResume

from .core import Base


class DBResume(Base):
    __tablename__ = "Resumes"

    id: Mapped[str] = mapped_column(primary_key=True, index=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("Users.id"), index=True)
    job_title: Mapped[str] = mapped_column(nullable=False)
    job_description: Mapped[str] = mapped_column(nullable=False)
    resume: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.now)


def create_resume(resume: CreateResume, session: Session) -> Resume:
    db_resume = DBResume(**resume.model_dump(exclude_none=True))
    session.add(db_resume)
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    session.refresh(db_resume)
    return Resume(**db_resume.__dict__)


def get_resume(resume_id: str, session: Session) -> Resume:
    db_resume = session.query(DBResume).filter(DBResume.id == resume_id).first()
    return Resume(**db_resume.__dict__)


def get_user_resumes(user_id: str, session: Session) -> list[Resume]:
    db_resumes = session.query(DBResume).filter(DBResume.user_id == user_id).all()
    return [Resume(**db_resume.__dict__) for db_resume in db_resumes]
