from abc import ABC, abstractmethod
from typing import List, Optional
from pydantic import BaseModel


class Word(BaseModel):
    """A word with timestamp information."""
    word: str
    start: float
    end: float
    probability: Optional[float] = None


class Segment(BaseModel):
    """A text segment with timestamp information."""
    start: float
    end: float
    text: str
    words: Optional[List[Word]] = None


class LyricsTranscriptionResult(BaseModel):
    """Result of lyrics transcription."""
    language: str
    text: str
    segments: List[Segment]
    words: List[Word]
    metadata: dict


class LyricsTranscriptionError(Exception):
    """Custom exception for lyrics transcription errors."""
    pass


class LyricsTranscriptionService(ABC):
    """Abstract base class for lyrics transcription services."""
    
    @abstractmethod
    def transcribe(self, vocals_path: str) -> LyricsTranscriptionResult:
        """
        Transcribe vocals to extract lyrics with timestamps.
        
        Args:
            vocals_path: Path to vocals WAV file
            
        Returns:
            LyricsTranscriptionResult containing transcribed lyrics with timestamps
            
        Raises:
            LyricsTranscriptionError: If transcription fails
        """
        pass
