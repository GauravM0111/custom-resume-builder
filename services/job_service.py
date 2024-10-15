from requests import Session
from models.jobs import Job, JobCreate, JobForm
from db.jobs import create_job as create_job_db


class JobService:
    def create_job(self, job_details: JobForm, db: Session) -> Job:
        if not job_details.title:
            job_details.title = "No title lololol"

        return create_job_db(JobCreate(**job_details.model_dump(exclude_none=True)), db)
