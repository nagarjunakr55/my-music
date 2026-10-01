from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.jobs.job_manager import job_manager
from app.services.real_processor import process_job_real
from app.models.job import JobStatus
import asyncio
import os
import shutil

router = APIRouter()

# Base directory for job data
JOBS_DIR = "data/jobs"


@router.post("/generate")
async def generate_song(
    song: UploadFile = File(...),
    lyrics: str = Form(...)
):
    """Generate a new song with replaced lyrics."""
    
    # Validate file type
    if not song.filename.lower().endswith(('.mp3', '.wav')):
        raise HTTPException(status_code=400, detail="Only MP3 and WAV files are supported")
    
    # Validate lyrics
    if not lyrics or not lyrics.strip():
        raise HTTPException(status_code=400, detail="Lyrics cannot be empty")
    
    # Create job
    job_id = job_manager.create_job()
    
    # Create job directory
    job_dir = os.path.join(JOBS_DIR, job_id)
    os.makedirs(job_dir, exist_ok=True)
    
    # Save uploaded file
    original_path = os.path.join(job_dir, "original.mp3")
    with open(original_path, "wb") as f:
        shutil.copyfileobj(song.file, f)
    
    # Save lyrics
    lyrics_path = os.path.join(job_dir, "lyrics.txt")
    with open(lyrics_path, "w") as f:
        f.write(lyrics)
    
    # Start background processing
    asyncio.create_task(process_job_real(job_id, original_path, job_dir))
    
    return {"jobId": job_id, "status": JobStatus.QUEUED}
