import asyncio
from app.jobs.job_manager import job_manager
from app.models.job import JobStatus, ProcessingStage


async def process_job_mock(job_id: str):
    """Mock processing that simulates the full pipeline with progress updates."""
    stages = [
        (ProcessingStage.UPLOAD_COMPLETE, 10),
        (ProcessingStage.NORMALIZING_AUDIO, 20),
        (ProcessingStage.SEPARATING_VOCALS, 50),
        (ProcessingStage.STEMS_READY, 55),
        (ProcessingStage.ANALYZING_MELODY, 70),
        (ProcessingStage.ALIGNING_LYRICS, 80),
        (ProcessingStage.GENERATING_VOCALS, 90),
        (ProcessingStage.MIXING, 95),
        (ProcessingStage.FINALIZING, 98),
        (ProcessingStage.COMPLETED, 100),
    ]
    
    try:
        job_manager.update_job(job_id, JobStatus.PROCESSING, ProcessingStage.UPLOAD_COMPLETE, 0)
        
        for stage, progress in stages:
            await asyncio.sleep(2)  # Simulate processing time
            job_manager.update_job(job_id, JobStatus.PROCESSING, stage, progress)
        
        job_manager.update_job(job_id, JobStatus.COMPLETED, ProcessingStage.COMPLETED, 100)
    except Exception as e:
        job_manager.update_job(job_id, JobStatus.FAILED, error=str(e))
