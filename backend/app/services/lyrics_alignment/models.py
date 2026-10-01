from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field


class TeluguUnit(BaseModel):
    """A single Telugu akshara (orthographic syllable) with timing information."""
    text: str = Field(..., description="The Telugu akshara text")
    start: float = Field(..., description="Start time in seconds")
    end: float = Field(..., description="End time in seconds")
    midi: Optional[int] = Field(None, description="MIDI note number")
    note_name: Optional[str] = Field(None, description="Note name (e.g., C4)")
    confidence: Optional[float] = Field(None, description="Confidence score")


class AlignedLine(BaseModel):
    """A line of lyrics aligned to a time range."""
    text: str = Field(..., description="Original line text")
    start: float = Field(..., description="Line start time in seconds")
    end: float = Field(..., description="Line end time in seconds")
    units: List[TeluguUnit] = Field(default_factory=list, description="Telugu units in this line")
    unit_count: int = Field(..., description="Number of Telugu units")
    line_index: int = Field(..., description="Line index in the lyrics")
    phrase_index: Optional[int] = Field(None, description="Index of the vocal phrase this line maps to")


class VocalPhrase(BaseModel):
    """A vocal phrase detected from melody analysis."""
    start: float = Field(..., description="Phrase start time in seconds")
    end: float = Field(..., description="Phrase end time in seconds")
    duration: float = Field(..., description="Phrase duration in seconds")
    note_count: int = Field(..., description="Number of notes in this phrase")
    avg_pitch: Optional[float] = Field(None, description="Average pitch in Hz")
    pitch_range: Optional[tuple[float, float]] = Field(None, description="Pitch range (min, max) in Hz")


class OriginalAlignment(BaseModel):
    """Original lyrics aligned with melody and timing."""
    text: str = Field(..., description="Full original lyrics text")
    lines: List[AlignedLine] = Field(..., description="Aligned lines")
    total_units: int = Field(..., description="Total number of Telugu units")
    line_count: int = Field(..., description="Number of lines")
    vocal_phrases: List[VocalPhrase] = Field(..., description="Detected vocal phrases")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class LineComparison(BaseModel):
    """Comparison between original and new lyrics for a single line."""
    original_text: str = Field(..., description="Original line text")
    new_text: str = Field(..., description="New line text")
    original_units: int = Field(..., description="Number of units in original line")
    new_units: int = Field(..., description="Number of units in new line")
    fit_status: Literal["GOOD", "TIGHT", "LOOSE", "POOR"] = Field(..., description="Fit assessment")
    line_index: int = Field(..., description="Line index")
    message: str = Field(..., description="Human-readable fit message")


class AlignedLyrics(BaseModel):
    """New lyrics aligned using original alignment as template."""
    original_text: str = Field(..., description="Original lyrics text")
    new_text: str = Field(..., description="New lyrics text")
    lines: List[AlignedLine] = Field(..., description="Aligned new lyrics lines")
    comparisons: List[LineComparison] = Field(..., description="Line-by-line comparisons")
    total_units: int = Field(..., description="Total number of units in new lyrics")
    line_count: int = Field(..., description="Number of lines")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class LyricsAlignmentRequest(BaseModel):
    """Request for lyrics alignment."""
    original_lyrics: str = Field(..., description="Original Telugu lyrics")
    new_lyrics: str = Field(..., description="New Telugu lyrics")
    melody_path: str = Field(..., description="Path to melody.json file")


class LyricsAlignmentResult(BaseModel):
    """Result of lyrics alignment process."""
    original_alignment: OriginalAlignment = Field(..., description="Original lyrics alignment")
    aligned_lyrics: AlignedLyrics = Field(..., description="New lyrics alignment")
    success: bool = Field(..., description="Whether alignment succeeded")
    message: str = Field(..., description="Status message")
