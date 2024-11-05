from datetime import datetime
from sqlalchemy.orm import Session, Mapped, mapped_column

from models.jobs import Job, JobCreate
from .core import Base
from uuid import uuid4


class DBJob(Base):
    __tablename__ = "Jobs"

    id: Mapped[str] = mapped_column(primary_key=True, index=True, default=lambda: str(uuid4()))
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=lambda: datetime.now())
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)


def create_job(job: JobCreate, session: Session) -> Job:
    db_job = DBJob(**job.model_dump(exclude_none=True))
    session.add(db_job)
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    session.refresh(db_job)
    return Job(**db_job.__dict__)
