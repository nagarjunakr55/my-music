import uuid
from typing import Dict, Optional
from app.models.job import JobStatus, ProcessingStage, JobResponse
import asyncio


class JobManager:
    def __init__(self):
        self.jobs: Dict[str, JobResponse] = {}
    
    def create_job(self) -> str:
        job_id = str(uuid.uuid4())
        self.jobs[job_id] = JobResponse(
            jobId=job_id,
            status=JobStatus.QUEUED
        )
        return job_id
    
    def get_job(self, job_id: str) -> Optional[JobResponse]:
        return self.jobs.get(job_id)
    
    def update_job(self, job_id: str, status: JobStatus, stage: Optional[ProcessingStage] = None, progress: Optional[int] = None, error: Optional[str] = None):
        if job_id in self.jobs:
            self.jobs[job_id].status = status
            if stage:
                self.jobs[job_id].stage = stage
            if progress is not None:
                self.jobs[job_id].progress = progress
            if error:
                self.jobs[job_id].error = error


job_manager = JobManager()
