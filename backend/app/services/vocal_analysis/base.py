from abc import ABC, abstractmethod
from typing import List, Optional
from pydantic import BaseModel


class Note(BaseModel):
    """A musical note extracted from vocals."""
    start: float  # Start time in seconds
    end: float  # End time in seconds
    duration: float  # Duration in seconds
    frequency: float  # Fundamental frequency in Hz
    midi: int  # MIDI note number
    note: str  # Note name (e.g., "C4")
    confidence: float  # Confidence score (0-1)


class VoicedRegion(BaseModel):
    """A region where vocals are present."""
    start: float  # Start time in seconds
    end: float  # End time in seconds
    duration: float  # Duration in seconds


class VocalAnalysisResult(BaseModel):
    """Result of vocal melody analysis."""
    duration: float  # Total audio duration in seconds
    notes: List[Note]  # List of detected notes
    voiced_regions: List[VoicedRegion]  # List of voiced regions
    metadata: dict  # Additional metadata (pitch range, statistics, etc.)


class VocalAnalysisError(Exception):
    """Custom exception for vocal analysis errors."""
    pass


class VocalAnalysisService(ABC):
    """Abstract base class for vocal analysis services."""
    
    @abstractmethod
    def analyze(self, vocals_path: str) -> VocalAnalysisResult:
        """
        Analyze vocals to extract melody information.
        
        Args:
            vocals_path: Path to vocals WAV file
            
        Returns:
            VocalAnalysisResult containing melody information
            
        Raises:
            VocalAnalysisError: If analysis fails
        """
        pass
