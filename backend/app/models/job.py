from pydantic import BaseModel
from typing import Optional
from enum import Enum


class JobStatus(str, Enum):
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ProcessingStage(str, Enum):
    UPLOAD_COMPLETE = "UPLOAD_COMPLETE"
    NORMALIZING_AUDIO = "NORMALIZING_AUDIO"
    SEPARATING_VOCALS = "SEPARATING_VOCALS"
    STEMS_READY = "STEMS_READY"
    ANALYZING_MELODY = "ANALYZING_MELODY"
    ALIGNING_LYRICS = "ALIGNING_LYRICS"
    GENERATING_VOCALS = "GENERATING_VOCALS"
    MIXING = "MIXING"
    FINALIZING = "FINALIZING"
    COMPLETED = "COMPLETED"


class JobResponse(BaseModel):
    jobId: str
    status: JobStatus
    stage: Optional[ProcessingStage] = None
    progress: Optional[int] = None
    error: Optional[str] = None


class GenerateRequest(BaseModel):
    lyrics: str
