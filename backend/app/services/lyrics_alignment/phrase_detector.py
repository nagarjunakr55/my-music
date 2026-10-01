import json
import os
from typing import List, Dict, Any, Tuple
import numpy as np
from app.services.lyrics_alignment.models import VocalPhrase


class PhraseDetectionError(Exception):
    """Custom exception for phrase detection errors."""
    pass


class VocalPhraseDetector:
    """Detect vocal phrases from melody analysis data."""
    
    def __init__(self, min_pause_duration: float = 0.5, min_phrase_duration: float = 1.0):
        """
        Initialize the vocal phrase detector.
        
        Args:
            min_pause_duration: Minimum silence duration to consider as a phrase boundary (seconds)
            min_phrase_duration: Minimum duration for a valid vocal phrase (seconds)
        """
        self.min_pause_duration = min_pause_duration
        self.min_phrase_duration = min_phrase_duration
    
    def detect_phrases_from_melody(self, melody_path: str) -> List[VocalPhrase]:
        """
        Detect vocal phrases from melody.json file.
        
        Args:
            melody_path: Path to melody.json file
            
        Returns:
            List of VocalPhrase objects
            
        Raises:
            PhraseDetectionError: If detection fails
        """
        if not os.path.exists(melody_path):
            raise PhraseDetectionError(f"Melody file not found: {melody_path}")
        
        try:
            with open(melody_path, 'r') as f:
                melody_data = json.load(f)
            return self.detect_phrases_from_notes(melody_data.get('notes', []))
            
        except json.JSONDecodeError as e:
            raise PhraseDetectionError(f"Failed to parse melody.json: {e}")
        except Exception as e:
            raise PhraseDetectionError(f"Failed to detect phrases: {e}")

    def detect_phrases_from_notes(self, notes: List[Dict[str, Any]]) -> List[VocalPhrase]:
        """Detect vocal phrases from an in-memory notes list."""
        if not notes:
            return []

        sorted_notes = sorted(notes, key=lambda x: x['start'])

        phrases = []
        current_phrase_notes = []
        last_end = None

        for note in sorted_notes:
            start = note['start']
            end = note['end']
            confidence = note.get('confidence', 1.0)

            if confidence < 0.3:
                continue

            if last_end is not None and (start - last_end) > self.min_pause_duration:
                if current_phrase_notes:
                    phrase = self._create_phrase_from_notes(current_phrase_notes)
                    if phrase.duration >= self.min_phrase_duration:
                        phrases.append(phrase)
                current_phrase_notes = []

            current_phrase_notes.append(note)
            last_end = end

        if current_phrase_notes:
            phrase = self._create_phrase_from_notes(current_phrase_notes)
            if phrase.duration >= self.min_phrase_duration:
                phrases.append(phrase)

        return phrases
    
    def _create_phrase_from_notes(self, notes: List[Dict[str, Any]]) -> VocalPhrase:
        """
        Create a VocalPhrase from a list of notes.
        
        Args:
            notes: List of note dictionaries
            
        Returns:
            VocalPhrase object
        """
        if not notes:
            raise ValueError("Cannot create phrase from empty notes list")
        
        start = min(note['start'] for note in notes)
        end = max(note['end'] for note in notes)
        duration = end - start
        
        # Calculate pitch statistics
        pitches = [note.get('midi', 0) for note in notes if note.get('midi') is not None]
        avg_pitch = np.mean(pitches) if pitches else None
        pitch_range = (min(pitches), max(pitches)) if pitches else None
        
        return VocalPhrase(
            start=start,
            end=end,
            duration=duration,
            note_count=len(notes),
            avg_pitch=avg_pitch,
            pitch_range=pitch_range
        )
    
    def get_phrase_boundaries(self, phrases: List[VocalPhrase]) -> List[Tuple[float, float]]:
        """
        Get phrase boundaries as (start, end) tuples.
        
        Args:
            phrases: List of VocalPhrase objects
            
        Returns:
            List of (start, end) tuples
        """
        return [(phrase.start, phrase.end) for phrase in phrases]


# Singleton instance
vocal_phrase_detector = VocalPhraseDetector()
