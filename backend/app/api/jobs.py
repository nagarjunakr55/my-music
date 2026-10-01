from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from app.jobs.job_manager import job_manager
from app.models.job import JobResponse
from app.services.lyrics_alignment import lyrics_alignment_service, LyricsAlignmentError
import os
import json
import time

router = APIRouter()

JOBS_DIR = "data/jobs"


class LyricsAlignmentRequest(BaseModel):
    original_lyrics: str
    new_lyrics: str


def get_existing_job_dir(job_id: str) -> str | None:
    job_dir = os.path.join(JOBS_DIR, job_id)
    if os.path.isdir(job_dir):
        return job_dir
    return None


@router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job(job_id: str):
    """Get the status of a job."""
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.get("/jobs/{job_id}/audio")
async def get_job_audio(job_id: str):
    """Get the generated audio file for a completed job."""
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.status.value != "COMPLETED":
        raise HTTPException(status_code=400, detail="Job is not completed yet")
    
    # For MVP, return the original file as placeholder
    # In real implementation, this would return the actual generated MP3 file
    job_dir = os.path.join(JOBS_DIR, job_id)
    original_path = os.path.join(job_dir, "original.mp3")
    
    if os.path.exists(original_path):
        return FileResponse(original_path, media_type="audio/mpeg", filename="generated-song.mp3")
    
    raise HTTPException(status_code=404, detail="Audio file not found")


@router.get("/jobs/{job_id}/stems/vocals")
async def get_job_stems_vocals(job_id: str):
    """Get the vocals stem for a completed job (debug endpoint)."""
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job_dir = os.path.join(JOBS_DIR, job_id)
    vocals_path = os.path.join(job_dir, "vocals.wav")
    
    if not os.path.exists(vocals_path):
        raise HTTPException(status_code=404, detail="Vocals stem not found")
    
    return FileResponse(vocals_path, media_type="audio/wav", filename="vocals.wav")


@router.get("/jobs/{job_id}/stems/instrumental")
async def get_job_stems_instrumental(job_id: str):
    """Get the instrumental stem for a completed job (debug endpoint)."""
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job_dir = os.path.join(JOBS_DIR, job_id)
    instrumental_path = os.path.join(job_dir, "instrumental.wav")
    
    if not os.path.exists(instrumental_path):
        raise HTTPException(status_code=404, detail="Instrumental stem not found")
    
    return FileResponse(instrumental_path, media_type="audio/wav", filename="instrumental.wav")


@router.get("/jobs/{job_id}/stems/original")
async def get_job_stems_original(job_id: str):
    """Get the original uploaded song (debug endpoint)."""
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job_dir = os.path.join(JOBS_DIR, job_id)
    original_path = os.path.join(job_dir, "original.mp3")
    
    if not os.path.exists(original_path):
        raise HTTPException(status_code=404, detail="Original file not found")
    
    return FileResponse(original_path, media_type="audio/mpeg", filename="original.mp3")


@router.get("/jobs/{job_id}/melody")
async def get_job_melody(job_id: str):
    """Get the melody analysis JSON for a completed job."""
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job_dir = os.path.join(JOBS_DIR, job_id)
    melody_path = os.path.join(job_dir, "analysis", "melody.json")
    
    if not os.path.exists(melody_path):
        raise HTTPException(status_code=404, detail="Melody analysis not found")
    
    with open(melody_path, 'r') as f:
        melody_data = json.load(f)
    
    return JSONResponse(content=melody_data)


@router.get("/jobs/{job_id}/lyrics")
async def get_job_lyrics(job_id: str):
    """Get the lyrics transcription JSON for a completed job."""
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job_dir = os.path.join(JOBS_DIR, job_id)
    lyrics_path = os.path.join(job_dir, "analysis", "lyrics.json")
    
    if not os.path.exists(lyrics_path):
        raise HTTPException(status_code=404, detail="Lyrics transcription not found")
    
    with open(lyrics_path, 'r') as f:
        lyrics_data = json.load(f)
    
    return JSONResponse(content=lyrics_data)


@router.post("/jobs/{job_id}/align-lyrics")
async def align_lyrics(job_id: str, request: LyricsAlignmentRequest):
    """Align original and new Telugu lyrics with melody timing."""
    api_start = time.time()

    job = job_manager.get_job(job_id)
    job_dir = get_existing_job_dir(job_id)

    if not job and not job_dir:
        raise HTTPException(status_code=404, detail="Job not found")

    if job and job.status.value != "COMPLETED":
        raise HTTPException(status_code=400, detail="Job is not completed yet")

    if not job_dir:
        raise HTTPException(status_code=404, detail="Job artifacts not found")

    melody_path = os.path.join(job_dir, "analysis", "melody.json")
    
    if not os.path.exists(melody_path):
        raise HTTPException(status_code=404, detail="Melody analysis not found")
    
    try:
        result = lyrics_alignment_service.process_alignment(
            original_lyrics=request.original_lyrics,
            new_lyrics=request.new_lyrics,
            melody_path=melody_path
        )
        
        if not result.success:
            raise HTTPException(status_code=400, detail=result.message)
        
        # Save alignment files
        write_start = time.time()
        analysis_dir = os.path.join(job_dir, "analysis")
        os.makedirs(analysis_dir, exist_ok=True)
        
        original_alignment_path = os.path.join(analysis_dir, "original_alignment.json")
        with open(original_alignment_path, 'w') as f:
            json.dump(result.original_alignment.model_dump(), f, indent=2)
        
        aligned_lyrics_path = os.path.join(analysis_dir, "aligned_lyrics.json")
        with open(aligned_lyrics_path, 'w') as f:
            json.dump(result.aligned_lyrics.model_dump(), f, indent=2)
        write_time = (time.time() - write_start) * 1000
        print(f"[PERF] Write JSON files: {write_time:.2f} ms")
        
        total_time = (time.time() - api_start) * 1000
        print(f"[PERF] API TOTAL response time: {total_time:.2f} ms")
        
        return JSONResponse(content=result.aligned_lyrics.model_dump())
        
    except LyricsAlignmentError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Alignment failed: {str(e)}")


@router.get("/jobs/{job_id}/original-alignment")
async def get_original_alignment(job_id: str):
    """Get the original lyrics alignment JSON."""
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job_dir = os.path.join(JOBS_DIR, job_id)
    alignment_path = os.path.join(job_dir, "analysis", "original_alignment.json")
    
    if not os.path.exists(alignment_path):
        raise HTTPException(status_code=404, detail="Original alignment not found")
    
    with open(alignment_path, 'r') as f:
        alignment_data = json.load(f)
    
    return JSONResponse(content=alignment_data)


@router.get("/jobs/{job_id}/aligned-lyrics")
async def get_aligned_lyrics(job_id: str):
    """Get the aligned new lyrics JSON."""
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job_dir = os.path.join(JOBS_DIR, job_id)
    aligned_lyrics_path = os.path.join(job_dir, "analysis", "aligned_lyrics.json")
    
    if not os.path.exists(aligned_lyrics_path):
        raise HTTPException(status_code=404, detail="Aligned lyrics not found")
    
    with open(aligned_lyrics_path, 'r') as f:
        aligned_lyrics_data = json.load(f)
    
    return JSONResponse(content=aligned_lyrics_data)
