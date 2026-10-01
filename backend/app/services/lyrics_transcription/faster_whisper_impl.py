import os
from typing import List, Optional
import whisper
import numpy as np
from app.services.lyrics_transcription.base import (
    LyricsTranscriptionService,
    LyricsTranscriptionResult,
    Word,
    Segment,
    LyricsTranscriptionError
)


class OpenAIWhisperLyricsTranscriptionService(LyricsTranscriptionService):
    """Lyrics transcription service using OpenAI Whisper."""
    
    def __init__(
        self,
        model_size: Optional[str] = None,
        device: str = "cpu",
        language: Optional[str] = None,
    ):
        """
        Initialize the OpenAI Whisper transcription service.
        
        Args:
            model_size: Model size (tiny, base, small, medium, large-v3). If None, reads from WHISPER_MODEL env var (default: small)
            device: Device to run on (cpu, cuda, auto)
            language: Language code (e.g., 'en', 'te') or None for auto-detect
        """
        self.model_size = model_size or os.getenv("WHISPER_MODEL", "small")
        self.device = device
        self.language = language
        self._model = None
        self._load_model()
    
    def _load_model(self):
        """Load the Whisper model."""
        try:
            self._model = whisper.load_model(self.model_size, device=self.device)
        except Exception as e:
            raise LyricsTranscriptionError(f"Failed to load Whisper model: {e}")
    
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
        if not os.path.exists(vocals_path):
            raise LyricsTranscriptionError(f"Vocals file not found: {vocals_path}")
        
        try:
            # Transcribe with word-level timestamps
            transcribe_kwargs = {
                "word_timestamps": True,
                "fp16": False  # Use float32 for CPU compatibility
            }
            
            # Add language if specified
            if self.language:
                transcribe_kwargs["language"] = self.language
            
            result = self._model.transcribe(vocals_path, **transcribe_kwargs)
            
            # Convert to our format
            segments_list = []
            words_list = []
            probabilities = []
            
            for segment in result["segments"]:
                segment_words = []
                if "words" in segment:
                    for word in segment["words"]:
                        word_obj = Word(
                            word=word["word"].strip(),
                            start=word["start"],
                            end=word["end"],
                            probability=word.get("probability")
                        )
                        words_list.append(word_obj)
                        segment_words.append(word_obj)
                        if word.get("probability") is not None:
                            probabilities.append(word["probability"])
                
                segment_obj = Segment(
                    start=segment["start"],
                    end=segment["end"],
                    text=segment["text"].strip(),
                    words=segment_words if segment_words else None
                )
                segments_list.append(segment_obj)
            
            # Calculate confidence statistics
            avg_probability = float(np.mean(probabilities)) if probabilities else 0.0
            median_probability = float(np.median(probabilities)) if probabilities else 0.0
            low_confidence_threshold = 0.3
            low_confidence_count = sum(1 for p in probabilities if p < low_confidence_threshold)
            
            # Calculate metadata
            metadata = {
                "model": self.model_size,
                "device": self.device,
                "detected_language": result["language"],
                "explicit_language": self.language,
                "duration": result.get("duration", 0),
                "segments_count": len(segments_list),
                "words_count": len(words_list),
                "avg_probability": avg_probability,
                "median_probability": median_probability,
                "low_confidence_count": low_confidence_count,
                "low_confidence_threshold": low_confidence_threshold,
            }
            
            return LyricsTranscriptionResult(
                language=result["language"],
                text=result["text"].strip(),
                segments=segments_list,
                words=words_list,
                metadata=metadata
            )
            
        except Exception as e:
            raise LyricsTranscriptionError(f"Transcription failed: {e}")


def get_lyrics_transcription_service(
    model_size: Optional[str] = None,
    device: str = "cpu",
    language: Optional[str] = None,
) -> LyricsTranscriptionService:
    """Get a lyrics transcription service instance."""
    return OpenAIWhisperLyricsTranscriptionService(
        model_size=model_size,
        device=device,
        language=language
    )
