import os
from typing import List, Optional
import numpy as np
from transformers import pipeline, AutomaticSpeechRecognitionPipeline
from app.services.lyrics_transcription.base import (
    LyricsTranscriptionService,
    LyricsTranscriptionResult,
    Word,
    Segment,
    LyricsTranscriptionError
)


class TeluguWhisperTranscriptionService(LyricsTranscriptionService):
    """Lyrics transcription service using BuzzASR/telugu (Telugu-specific Whisper)."""
    
    def __init__(
        self,
        model_id: str = "BuzzASR/telugu",
        device: str = "cpu",
        language: str = "te",
    ):
        """
        Initialize the Telugu Whisper transcription service.
        
        Args:
            model_id: Hugging Face model ID (default: BuzzASR/telugu)
            device: Device to run on (cpu, cuda, auto)
            language: Language code (default: te for Telugu)
        """
        self.model_id = model_id
        self.device = device
        self.language = language
        self._pipeline = None
        self._load_model()
    
    def _load_model(self):
        """Load the Telugu Whisper model from Hugging Face."""
        try:
            self._pipeline = pipeline(
                task="automatic-speech-recognition",
                model=self.model_id,
                chunk_length_s=30,
                device=self.device
            )
            # Force Telugu language for transcription
            self._pipeline.model.config.forced_decoder_ids = (
                self._pipeline.tokenizer.get_decoder_prompt_ids(
                    language=self.language,
                    task="transcribe"
                )
            )
        except Exception as e:
            raise LyricsTranscriptionError(f"Failed to load Telugu Whisper model: {e}")
    
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
            # Transcribe with timestamps
            result = self._pipeline(
                vocals_path,
                return_timestamps="word",  # Request word-level timestamps
                generate_kwargs={"language": self.language}
            )
            
            # Convert to our format
            segments_list = []
            words_list = []
            probabilities = []
            
            # Handle different result formats from transformers
            if isinstance(result, dict):
                text = result.get("text", "").strip()
                chunks = result.get("chunks", [])
                
                for chunk in chunks:
                    # Extract timestamp information
                    timestamp = chunk.get("timestamp", None)
                    if timestamp and len(timestamp) == 2:
                        start, end = timestamp
                    else:
                        start, end = 0, 0
                    
                    chunk_text = chunk.get("text", "").strip()
                    if not chunk_text:
                        continue
                    
                    # Create segment
                    segment_obj = Segment(
                        start=start,
                        end=end,
                        text=chunk_text,
                        words=None  # Word-level timestamps may not be available
                    )
                    segments_list.append(segment_obj)
                    
                    # For now, treat each chunk as a "word" for compatibility
                    # TODO: Investigate if true word-level timestamps are available
                    word_obj = Word(
                        word=chunk_text,
                        start=start,
                        end=end,
                        probability=None  # Probability may not be available
                    )
                    words_list.append(word_obj)
            
            # Calculate confidence statistics (limited availability with this model)
            avg_probability = 0.0
            median_probability = 0.0
            low_confidence_count = 0
            low_confidence_threshold = 0.3
            
            # Calculate metadata
            metadata = {
                "model": self.model_id,
                "device": self.device,
                "detected_language": self.language,
                "explicit_language": self.language,
                "duration": 0,  # Not directly available from pipeline
                "segments_count": len(segments_list),
                "words_count": len(words_list),
                "avg_probability": avg_probability,
                "median_probability": median_probability,
                "low_confidence_count": low_confidence_count,
                "low_confidence_threshold": low_confidence_threshold,
                "note": "Word-level probabilities not available from this model"
            }
            
            return LyricsTranscriptionResult(
                language=self.language,
                text=text,
                segments=segments_list,
                words=words_list,
                metadata=metadata
            )
            
        except Exception as e:
            raise LyricsTranscriptionError(f"Transcription failed: {e}")


def get_telugu_lyrics_transcription_service(
    model_id: Optional[str] = None,
    device: str = "cpu",
    language: str = "te",
) -> LyricsTranscriptionService:
    """Get a Telugu lyrics transcription service instance."""
    return TeluguWhisperTranscriptionService(
        model_id=model_id or "vasista22/whisper-telugu-small",
        device=device,
        language=language
    )
