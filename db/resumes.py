from uuid import uuid4
from sqlalchemy.orm import Session, Mapped, mapped_column
from sqlalchemy import JSON, ForeignKey

from models.resumes import Resume, CreateResume

from .core import Base


class DBResume(Base):
    __tablename__ = "Resumes"

    id: Mapped[str] = mapped_column(primary_key=True, index=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("Users.id"), index=True)
    job_id: Mapped[str] = mapped_column(ForeignKey("Jobs.id"))
    resume: Mapped[dict] = mapped_column(JSON, nullable=False)


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
