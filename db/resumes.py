from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import JSON, ForeignKey
from sqlalchemy.orm import Mapped, Session, mapped_column

from models.resumes import CreateResume, Resume, Theme, UpdateResume

from .core import Base, NotFoundError


class DBResume(Base):
    __tablename__ = "Resumes"

    id: Mapped[str] = mapped_column(
        primary_key=True, index=True, default=lambda: str(uuid4())
    )
    user_id: Mapped[str] = mapped_column(ForeignKey("Users.id"), index=True)
    job_title: Mapped[str] = mapped_column(nullable=False)
    job_description: Mapped[str] = mapped_column(nullable=False)
    resume: Mapped[dict] = mapped_column(JSON, nullable=False)
    theme: Mapped[Theme] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, default=lambda: datetime.now(timezone.utc)
    )


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


def update_resume(resume: UpdateResume, session: Session) -> Resume:
    db_resume = session.query(DBResume).filter(DBResume.id == resume.id).first()

    if not db_resume:
        raise NotFoundError(f"Resume with id {resume.id} not found")

    for k, v in resume.model_dump(exclude="id", exclude_none=True).items():
        setattr(db_resume, k, v)

    try:
        session.commit()
    except Exception as e:
        session.rollback()
        raise e

    session.refresh(db_resume)
    return Resume(**db_resume.__dict__)


def get_resume(resume_id: str, session: Session) -> Resume:
    db_resume = session.query(DBResume).filter(DBResume.id == resume_id).first()

    if not db_resume:
        raise NotFoundError(f"Resume with id {resume_id} not found")

    return Resume(**db_resume.__dict__)


def get_user_resumes(user_id: str, session: Session) -> list[Resume]:
    db_resumes = session.query(DBResume).filter(DBResume.user_id == user_id).all()
    return [Resume(**db_resume.__dict__) for db_resume in db_resumes]


def delete_resume(resume_id: str, session: Session) -> bool:
    resume_deleted = session.query(DBResume).filter(DBResume.id == resume_id).delete()

    try:
        session.commit()
    except Exception as e:
        session.rollback()
        raise e

    return resume_deleted > 0
