from sqlalchemy.orm import Session, Mapped, mapped_column
from sqlalchemy import JSON, ForeignKey

from models.resumes import Resume

from .core import Base


class DBResume(Base):
    __tablename__ = "Resumes"

    user_id: Mapped[str] = mapped_column(ForeignKey("Users.id"), primary_key=True, index=True)
    job_id: Mapped[str] = mapped_column(ForeignKey("Jobs.id"), primary_key=True, index=True)
    resume: Mapped[dict] = mapped_column(JSON, nullable=False)


def create_resume(resume: Resume, session: Session) -> Resume:
    db_resume = DBResume(**resume.model_dump(exclude_none=True))
    session.add(db_resume)
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    session.refresh(db_resume)
    return Resume(**db_resume.__dict__)