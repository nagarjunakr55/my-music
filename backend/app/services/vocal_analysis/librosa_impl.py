import os
import numpy as np
import librosa
from typing import List, Tuple, Optional
from app.services.vocal_analysis.base import (
    VocalAnalysisService, 
    VocalAnalysisResult, 
    Note, 
    VoicedRegion,
    VocalAnalysisError
)


class LibrosaVocalAnalysisService(VocalAnalysisService):
    """Vocal analysis service using librosa.pyin for pitch detection."""
    
    def __init__(
        self,
        fmin: float = 80.0,  # Minimum frequency (E2)
        fmax: float = 1000.0,  # Maximum frequency (B5)
        hop_length: int = 512,  # Hop length for analysis
        min_note_duration: float = 0.1,  # Minimum note duration in seconds
        max_note_duration: float = 10.0,  # Maximum note duration in seconds
        pitch_tolerance_cents: float = 50.0,  # Pitch tolerance for note segmentation (cents)
    ):
        """
        Initialize the librosa-based vocal analysis service.
        
        Args:
            fmin: Minimum frequency to detect (Hz)
            fmax: Maximum frequency to detect (Hz)
            hop_length: Hop length for STFT analysis
            min_note_duration: Minimum duration for a note (seconds)
            max_note_duration: Maximum duration for a note (seconds)
            pitch_tolerance_cents: Pitch tolerance for note segmentation (cents)
        """
        self.fmin = fmin
        self.fmax = fmax
        self.hop_length = hop_length
        self.min_note_duration = min_note_duration
        self.max_note_duration = max_note_duration
        self.pitch_tolerance_cents = pitch_tolerance_cents
    
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
        if not os.path.exists(vocals_path):
            raise VocalAnalysisError(f"Vocals file not found: {vocals_path}")
        
        try:
            # Load audio
            y, sr = librosa.load(vocals_path, sr=None, mono=True)
            duration = len(y) / sr
            
            # Extract F0 using pYIN
            f0, voiced_flag, voiced_probs = librosa.pyin(
                y,
                fmin=self.fmin,
                fmax=self.fmax,
                sr=sr,
                hop_length=self.hop_length,
                frame_length=2048,
                fill_na=np.nan
            )
            
            # Get time stamps
            times = librosa.times_like(f0, sr=sr, hop_length=self.hop_length)
            
            # Extract voiced regions
            voiced_regions = self._extract_voiced_regions(times, voiced_flag)
            
            # Segment notes from F0
            notes = self._segment_notes(times, f0, voiced_flag, voiced_probs)
            
            # Calculate metadata
            metadata = self._calculate_metadata(notes, voiced_regions, duration)
            
            return VocalAnalysisResult(
                duration=duration,
                notes=notes,
                voiced_regions=voiced_regions,
                metadata=metadata
            )
            
        except Exception as e:
            raise VocalAnalysisError(f"Vocal analysis failed: {e}")
    
    def _extract_voiced_regions(
        self, 
        times: np.ndarray, 
        voiced_flag: np.ndarray
    ) -> List[VoicedRegion]:
        """
        Extract continuous voiced regions from voiced flags.
        
        Args:
            times: Time stamps for each frame
            voiced_flag: Boolean array indicating voiced frames
            
        Returns:
            List of VoicedRegion objects
        """
        regions = []
        in_region = False
        region_start = 0.0
        
        for i, (t, voiced) in enumerate(zip(times, voiced_flag)):
            if voiced and not in_region:
                # Start of a new voiced region
                in_region = True
                region_start = t
            elif not voiced and in_region:
                # End of voiced region
                in_region = False
                region_end = t
                duration = region_end - region_start
                if duration >= self.min_note_duration:
                    regions.append(VoicedRegion(
                        start=region_start,
                        end=region_end,
                        duration=duration
                    ))
        
        # Handle case where audio ends while still voiced
        if in_region:
            region_end = times[-1]
            duration = region_end - region_start
            if duration >= self.min_note_duration:
                regions.append(VoicedRegion(
                    start=region_start,
                    end=region_end,
                    duration=duration
                ))
        
        return regions
    
    def _segment_notes(
        self,
        times: np.ndarray,
        f0: np.ndarray,
        voiced_flag: np.ndarray,
        voiced_probs: np.ndarray
    ) -> List[Note]:
        """
        Segment continuous F0 into discrete notes.
        
        Args:
            times: Time stamps for each frame
            f0: Fundamental frequency values
            voiced_flag: Boolean array indicating voiced frames
            voiced_probs: Voicing probabilities
            
        Returns:
            List of Note objects
        """
        notes = []
        
        # Filter to only voiced frames
        voiced_indices = np.where(voiced_flag)[0]
        if len(voiced_indices) == 0:
            return notes
        
        # Group consecutive voiced frames into potential notes
        note_segments = self._group_consecutive_voiced(voiced_indices, times, f0, voiced_probs)
        
        # Merge segments with similar pitch
        notes = self._merge_similar_segments(note_segments)
        
        return notes
    
    def _group_consecutive_voiced(
        self,
        voiced_indices: np.ndarray,
        times: np.ndarray,
        f0: np.ndarray,
        voiced_probs: np.ndarray
    ) -> List[dict]:
        """
        Group consecutive voiced frames into segments.
        
        Args:
            voiced_indices: Indices of voiced frames
            times: Time stamps
            f0: Frequency values
            voiced_probs: Voicing probabilities
            
        Returns:
            List of segment dictionaries
        """
        segments = []
        
        if len(voiced_indices) == 0:
            return segments
        
        # Find gaps in voiced frames
        gaps = np.where(np.diff(voiced_indices) > 1)[0]
        
        # Split at gaps
        split_indices = np.split(voiced_indices, gaps + 1)
        
        for indices in split_indices:
            if len(indices) == 0:
                continue
            
            segment_times = times[indices]
            segment_f0 = f0[indices]
            segment_probs = voiced_probs[indices]
            
            # Filter out NaN F0 values
            valid_mask = ~np.isnan(segment_f0)
            if not np.any(valid_mask):
                continue
            
            segment_times = segment_times[valid_mask]
            segment_f0 = segment_f0[valid_mask]
            segment_probs = segment_probs[valid_mask]
            
            if len(segment_f0) == 0:
                continue
            
            # Calculate median frequency for the segment
            median_freq = np.median(segment_f0)
            avg_confidence = np.mean(segment_probs)
            
            segments.append({
                'start': segment_times[0],
                'end': segment_times[-1],
                'duration': segment_times[-1] - segment_times[0],
                'frequency': median_freq,
                'confidence': avg_confidence,
                'f0_values': segment_f0,
                'times': segment_times
            })
        
        return segments
    
    def _merge_similar_segments(self, segments: List[dict]) -> List[Note]:
        """
        Merge segments with similar pitch into notes.
        
        Args:
            segments: List of segment dictionaries
            
        Returns:
            List of Note objects
        """
        if not segments:
            return []
        
        notes = []
        current_note = segments[0].copy()
        
        for segment in segments[1:]:
            # Check if segments are close in time
            gap = segment['start'] - current_note['end']
            
            # Check if pitches are similar (within tolerance)
            freq_ratio = segment['frequency'] / current_note['frequency']
            cents = 1200 * np.log2(freq_ratio)
            
            # Merge if gap is small and pitch is similar
            if gap < 0.2 and abs(cents) < self.pitch_tolerance_cents:
                # Merge segments
                current_note['end'] = segment['end']
                current_note['duration'] = current_note['end'] - current_note['start']
                # Update frequency as weighted average
                total_duration = current_note['duration'] + segment['duration']
                current_note['frequency'] = (
                    (current_note['frequency'] * current_note['duration'] + 
                     segment['frequency'] * segment['duration']) / total_duration
                )
                current_note['confidence'] = (
                    (current_note['confidence'] * current_note['duration'] + 
                     segment['confidence'] * segment['duration']) / total_duration
                )
            else:
                # Finalize current note
                if current_note['duration'] >= self.min_note_duration:
                    note = self._create_note_from_segment(current_note)
                    if note:
                        notes.append(note)
                # Start new note
                current_note = segment.copy()
        
        # Don't forget the last note
        if current_note['duration'] >= self.min_note_duration:
            note = self._create_note_from_segment(current_note)
            if note:
                notes.append(note)
        
        return notes
    
    def _create_note_from_segment(self, segment: dict) -> Optional[Note]:
        """
        Create a Note object from a segment.
        
        Args:
            segment: Segment dictionary
            
        Returns:
            Note object or None if invalid
        """
        frequency = segment['frequency']
        
        # Skip if frequency is out of range
        if frequency < self.fmin or frequency > self.fmax:
            return None
        
        # Convert to MIDI
        midi = self._hz_to_midi(frequency)
        
        # Get note name
        note_name = self._midi_to_note_name(midi)
        
        return Note(
            start=segment['start'],
            end=segment['end'],
            duration=segment['duration'],
            frequency=frequency,
            midi=midi,
            note=note_name,
            confidence=segment['confidence']
        )
    
    def _hz_to_midi(self, frequency: float) -> int:
        """
        Convert frequency to MIDI note number.
        
        Args:
            frequency: Frequency in Hz
            
        Returns:
            MIDI note number
        """
        return int(round(69 + 12 * np.log2(frequency / 440.0)))
    
    def _midi_to_note_name(self, midi: int) -> str:
        """
        Convert MIDI note number to note name.
        
        Args:
            midi: MIDI note number
            
        Returns:
            Note name (e.g., "C4")
        """
        notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        octave = (midi // 12) - 1
        note = notes[midi % 12]
        return f"{note}{octave}"
    
    def _calculate_metadata(
        self,
        notes: List[Note],
        voiced_regions: List[VoicedRegion],
        duration: float
    ) -> dict:
        """
        Calculate metadata about the analysis.
        
        Args:
            notes: List of detected notes
            voiced_regions: List of voiced regions
            duration: Total audio duration
            
        Returns:
            Dictionary with metadata
        """
        if not notes:
            return {
                'note_count': 0,
                'voiced_duration': 0.0,
                'voiced_ratio': 0.0,
                'pitch_range_hz': (0.0, 0.0),
                'pitch_range_semitones': (0, 0),
                'lowest_note': None,
                'highest_note': None,
            }
        
        frequencies = [note.frequency for note in notes]
        voiced_duration = sum(region.duration for region in voiced_regions)
        
        lowest_freq = min(frequencies)
        highest_freq = max(frequencies)
        
        lowest_midi = self._hz_to_midi(lowest_freq)
        highest_midi = self._hz_to_midi(highest_freq)
        
        return {
            'note_count': len(notes),
            'voiced_duration': voiced_duration,
            'voiced_ratio': voiced_duration / duration if duration > 0 else 0.0,
            'pitch_range_hz': (lowest_freq, highest_freq),
            'pitch_range_semitones': (lowest_midi, highest_midi),
            'lowest_note': self._midi_to_note_name(lowest_midi),
            'highest_note': self._midi_to_note_name(highest_midi),
        }


def get_vocal_analysis_service() -> VocalAnalysisService:
    """Get a vocal analysis service instance."""
    return LibrosaVocalAnalysisService()
