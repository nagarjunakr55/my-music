import json
import os
import time
from typing import List, Dict, Any, Optional, Literal
from app.services.lyrics_alignment.models import (
    AlignedLine, TeluguUnit, OriginalAlignment, VocalPhrase,
    LineComparison, AlignedLyrics, LyricsAlignmentResult
)
from app.services.lyrics_alignment.telugu_segmentation import telugu_segmentation_service
from app.services.lyrics_alignment.phrase_detector import vocal_phrase_detector

FitStatus = Literal["GOOD", "TIGHT", "LOOSE", "POOR"]


class LyricsAlignmentError(Exception):
    """Custom exception for lyrics alignment errors."""
    pass


class LyricsAlignmentService:
    """Service for aligning Telugu lyrics with melody and timing."""
    
    def __init__(self):
        """Initialize the lyrics alignment service."""
        self.segmentation = telugu_segmentation_service
        self.phrase_detector = vocal_phrase_detector
    
    def align_original_lyrics(
        self,
        original_lyrics: str,
        melody_path: str
    ) -> OriginalAlignment:
        """
        Align original Telugu lyrics with melody and timing.
        
        Args:
            original_lyrics: Original Telugu lyrics text
            melody_path: Path to melody.json file
            
        Returns:
            OriginalAlignment object
            
        Raises:
            LyricsAlignmentError: If alignment fails
        """
        total_start = time.time()
        
        try:
            load_start = time.time()
            with open(melody_path, 'r') as f:
                melody_data = json.load(f)
            notes = melody_data.get('notes', [])
            load_time = (time.time() - load_start) * 1000
            print(f"[PERF] Load melody.json: {load_time:.2f} ms")

            # Segment lyrics with structure
            seg_start = time.time()
            segmented = self.segmentation.segment_lyrics_with_structure(original_lyrics)
            lines = segmented['lines']
            seg_time = (time.time() - seg_start) * 1000
            print(f"[PERF] Telugu segmentation: {seg_time:.2f} ms")
            
            # Detect vocal phrases from already-loaded melody notes
            phrase_start = time.time()
            phrases = self.phrase_detector.detect_phrases_from_notes(notes)
            phrase_time = (time.time() - phrase_start) * 1000
            print(f"[PERF] Phrase detection: {phrase_time:.2f} ms")
            
            # Map lines to phrases
            map_start = time.time()
            aligned_lines = self._map_lines_to_phrases(lines, phrases, notes)
            map_time = (time.time() - map_start) * 1000
            print(f"[PERF] Map lines to phrases: {map_time:.2f} ms")
            
            # Distribute timing within each line
            dist_start = time.time()
            for line in aligned_lines:
                if line.units:
                    self._distribute_timing_in_line(line, notes)
            dist_time = (time.time() - dist_start) * 1000
            print(f"[PERF] Distribute timing: {dist_time:.2f} ms")
            
            total_time = (time.time() - total_start) * 1000
            print(f"[PERF] Original alignment TOTAL: {total_time:.2f} ms")
            
            return OriginalAlignment(
                text=original_lyrics,
                lines=aligned_lines,
                total_units=sum(line.unit_count for line in aligned_lines),
                line_count=len(aligned_lines),
                vocal_phrases=phrases,
                metadata={
                    'melody_path': melody_path,
                    'phrase_count': len(phrases)
                }
            )
            
        except Exception as e:
            raise LyricsAlignmentError(f"Failed to align original lyrics: {e}")
    
    def _map_lines_to_phrases(
        self,
        lines: List[Dict[str, Any]],
        phrases: List[VocalPhrase],
        notes: List[Dict[str, Any]]
    ) -> List[AlignedLine]:
        """
        Map lyric lines to vocal phrases.
        
        This is a heuristic mapping that tries to match lines to phrases
        based on timing and line count.
        
        Args:
            lines: Segmented lyric lines
            phrases: Detected vocal phrases
            notes: Melody notes
            
        Returns:
            List of AlignedLine objects
        """
        aligned_lines = []
        
        # Filter out empty lines for mapping
        non_empty_lines = [(i, line) for i, line in enumerate(lines) if line['text']]
        
        if not phrases:
            # No phrases detected - distribute evenly across song duration
            song_duration = max((note['end'] for note in notes), default=0)
            if song_duration > 0:
                duration_per_line = song_duration / max(len(non_empty_lines), 1)
                for i, (line_idx, line) in enumerate(non_empty_lines):
                    start = i * duration_per_line
                    end = (i + 1) * duration_per_line
                    aligned_lines.append(self._create_aligned_line(
                        line, line_idx, start, end, None, notes
                    ))
            return aligned_lines
        
        # Map lines to phrases
        # If we have more lines than phrases, some phrases will contain multiple lines
        # If we have more phrases than lines, some lines will span multiple phrases
        
        if len(non_empty_lines) <= len(phrases):
            # One or more phrases per line (or exact match)
            for i, (line_idx, line) in enumerate(non_empty_lines):
                if i < len(phrases):
                    phrase = phrases[i]
                    aligned_lines.append(self._create_aligned_line(
                        line, line_idx, phrase.start, phrase.end, i, notes
                    ))
        else:
            # Multiple lines per phrase
            phrase_idx = 0
            lines_in_current_phrase = 0
            lines_per_phrase = len(non_empty_lines) / len(phrases)
            
            for i, (line_idx, line) in enumerate(non_empty_lines):
                target_phrase_idx = int(i / lines_per_phrase)
                if target_phrase_idx < len(phrases):
                    phrase = phrases[target_phrase_idx]
                    # Distribute phrase time among lines
                    lines_in_this_phrase = int((target_phrase_idx + 1) * lines_per_phrase) - int(target_phrase_idx * lines_per_phrase)
                    line_idx_in_phrase = i - int(target_phrase_idx * lines_per_phrase)
                    
                    phrase_duration = phrase.end - phrase.start
                    line_duration = phrase_duration / max(lines_in_this_phrase, 1)
                    
                    start = phrase.start + line_idx_in_phrase * line_duration
                    end = start + line_duration
                    
                    aligned_lines.append(self._create_aligned_line(
                        line, line_idx, start, end, target_phrase_idx, notes
                    ))
        
        # Re-sort by line index to maintain original order
        aligned_lines.sort(key=lambda x: x.line_index)
        
        return aligned_lines
    
    def _create_aligned_line(
        self,
        line: Dict[str, Any],
        line_index: int,
        start: float,
        end: float,
        phrase_index: Optional[int],
        notes: List[Dict[str, Any]]
    ) -> AlignedLine:
        """
        Create an AlignedLine from segmented line data.
        
        Args:
            line: Segmented line data
            line_index: Line index
            start: Line start time
            end: Line end time
            phrase_index: Phrase index (if mapped)
            notes: Melody notes
            
        Returns:
            AlignedLine object
        """
        # Create Telugu units (without timing initially)
        units = []
        for akshara in line['aksharas']:
            units.append(TeluguUnit(
                text=akshara,
                start=0,  # Will be filled in by _distribute_timing_in_line
                end=0,
                midi=None,
                note_name=None,
                confidence=None
            ))
        
        return AlignedLine(
            text=line['text'],
            start=start,
            end=end,
            units=units,
            unit_count=len(units),
            line_index=line_index,
            phrase_index=phrase_index
        )
    
    def _distribute_timing_in_line(
        self,
        line: AlignedLine,
        notes: List[Dict[str, Any]]
    ):
        """
        Distribute timing across Telugu units within a line.
        
        Args:
            line: AlignedLine to distribute timing for
            notes: Melody notes
        """
        if not line.units:
            return
        
        # Find notes that fall within this line's time range
        line_notes = [
            note for note in notes
            if note['start'] >= line.start and note['end'] <= line.end
        ]
        
        if not line_notes:
            # No notes in this line - distribute evenly
            duration = line.end - line.start
            unit_duration = duration / len(line.units)
            for i, unit in enumerate(line.units):
                unit.start = line.start + i * unit_duration
                unit.end = unit.start + unit_duration
            return
        
        # Distribute units across notes
        # If more units than notes, some notes will have multiple units
        # If more notes than units, some units will span multiple notes
        
        if len(line.units) <= len(line_notes):
            # One or more notes per unit
            notes_per_unit = len(line_notes) / len(line.units)
            for i, unit in enumerate(line.units):
                start_note_idx = int(i * notes_per_unit)
                end_note_idx = int((i + 1) * notes_per_unit)
                unit_notes = line_notes[start_note_idx:end_note_idx]
                
                if unit_notes:
                    unit.start = unit_notes[0]['start']
                    unit.end = unit_notes[-1]['end']
                    # Assign MIDI from first note
                    unit.midi = unit_notes[0].get('midi')
                    unit.note_name = unit_notes[0].get('note_name')
                    unit.confidence = unit_notes[0].get('confidence')
        else:
            # Multiple units per note
            units_per_note = len(line.units) / len(line_notes)
            for i, note in enumerate(line_notes):
                start_unit_idx = int(i * units_per_note)
                end_unit_idx = int((i + 1) * units_per_note)
                unit_indices = range(start_unit_idx, min(end_unit_idx, len(line.units)))
                
                unit_count = len(list(unit_indices))
                if unit_count > 0:
                    note_duration = note['end'] - note['start']
                    unit_duration = note_duration / unit_count
                    
                    for j, unit_idx in enumerate(unit_indices):
                        unit = line.units[unit_idx]
                        unit.start = note['start'] + j * unit_duration
                        unit.end = unit.start + unit_duration
                        unit.midi = note.get('midi')
                        unit.note_name = note.get('note_name')
                        unit.confidence = note.get('confidence')
    
    def calculate_fit_status(self, original_count: int, new_count: int) -> FitStatus:
        """
        Calculate fit status for comparing original and new lyrics.
        
        Args:
            original_count: Number of units in original line
            new_count: Number of units in new line
            
        Returns:
            FitStatus (GOOD, TIGHT, LOOSE, POOR)
        """
        if original_count == 0:
            return "GOOD"
        
        ratio = new_count / original_count
        
        if 0.9 <= ratio <= 1.1:
            return "GOOD"
        elif 0.7 <= ratio < 0.9:
            return "TIGHT"
        elif 1.1 < ratio <= 1.3:
            return "LOOSE"
        else:
            return "POOR"
    
    def get_fit_message(self, fit_status: FitStatus, original_count: int, new_count: int) -> str:
        """
        Get human-readable fit message.
        
        Args:
            fit_status: Fit status
            original_count: Original unit count
            new_count: New unit count
            
        Returns:
            Human-readable message
        """
        if fit_status == "GOOD":
            return "✓ Good fit"
        elif fit_status == "TIGHT":
            return "⚠ This line has fewer syllables than the original"
        elif fit_status == "LOOSE":
            return "⚠ This line has more syllables than the original"
        else:  # POOR
            return f"⚠ This line has significantly different syllable count ({new_count} vs {original_count})"
    
    def align_new_lyrics(
        self,
        original_alignment: OriginalAlignment,
        new_lyrics: str
    ) -> AlignedLyrics:
        """
        Align new lyrics using original alignment as template.
        
        Args:
            original_alignment: Original lyrics alignment
            new_lyrics: New Telugu lyrics text
            
        Returns:
            AlignedLyrics object
            
        Raises:
            LyricsAlignmentError: If alignment fails
        """
        total_start = time.time()
        
        try:
            # Segment new lyrics
            seg_start = time.time()
            new_segmented = self.segmentation.segment_lyrics_with_structure(new_lyrics)
            new_lines = new_segmented['lines']
            seg_time = (time.time() - seg_start) * 1000
            print(f"[PERF] New lyrics segmentation: {seg_time:.2f} ms")
            
            # Compare line by line
            comp_start = time.time()
            comparisons = []
            aligned_new_lines = []
            
            for i, (orig_line, new_line) in enumerate(zip(original_alignment.lines, new_lines)):
                if not new_line['text']:
                    # Empty line - preserve timing but no units
                    aligned_new_lines.append(AlignedLine(
                        text='',
                        start=orig_line.start,
                        end=orig_line.end,
                        units=[],
                        unit_count=0,
                        line_index=i,
                        phrase_index=orig_line.phrase_index
                    ))
                    comparisons.append(LineComparison(
                        original_text=orig_line.text,
                        new_text='',
                        original_units=orig_line.unit_count,
                        new_units=0,
                        fit_status="GOOD",
                        line_index=i,
                        message="Empty line"
                    ))
                    continue
                
                # Calculate fit status
                fit_status = self.calculate_fit_status(orig_line.unit_count, new_line['count'])
                message = self.get_fit_message(fit_status, orig_line.unit_count, new_line['count'])
                
                comparisons.append(LineComparison(
                    original_text=orig_line.text,
                    new_text=new_line['text'],
                    original_units=orig_line.unit_count,
                    new_units=new_line['count'],
                    fit_status=fit_status,
                    line_index=i,
                    message=message
                ))
                
                # Create new units with timing from original
                new_units = []
                if orig_line.units:
                    # Distribute new units across original timing
                    if len(new_line['aksharas']) <= len(orig_line.units):
                        # One or more original units per new unit
                        orig_per_new = len(orig_line.units) / len(new_line['aksharas'])
                        for j, akshara in enumerate(new_line['aksharas']):
                            start_idx = int(j * orig_per_new)
                            end_idx = int((j + 1) * orig_per_new)
                            orig_units_slice = orig_line.units[start_idx:end_idx]
                            
                            if orig_units_slice:
                                new_units.append(TeluguUnit(
                                    text=akshara,
                                    start=orig_units_slice[0].start,
                                    end=orig_units_slice[-1].end,
                                    midi=orig_units_slice[0].midi,
                                    note_name=orig_units_slice[0].note_name,
                                    confidence=orig_units_slice[0].confidence
                                ))
                    else:
                        # Multiple new units per original unit
                        new_per_orig = len(new_line['aksharas']) / len(orig_line.units)
                        for j, orig_unit in enumerate(orig_line.units):
                            start_idx = int(j * new_per_orig)
                            end_idx = int((j + 1) * new_per_orig)
                            akshara_indices = range(start_idx, min(end_idx, len(new_line['aksharas'])))
                            
                            akshara_count = len(list(akshara_indices))
                            if akshara_count > 0:
                                unit_duration = (orig_unit.end - orig_unit.start) / akshara_count
                                for k, akshara_idx in enumerate(akshara_indices):
                                    new_units.append(TeluguUnit(
                                        text=new_line['aksharas'][akshara_idx],
                                        start=orig_unit.start + k * unit_duration,
                                        end=orig_unit.start + (k + 1) * unit_duration,
                                        midi=orig_unit.midi,
                                        note_name=orig_unit.note_name,
                                        confidence=orig_unit.confidence
                                    ))
                else:
                    # No original units - distribute evenly
                    duration = orig_line.end - orig_line.start
                    unit_duration = duration / len(new_line['aksharas'])
                    for j, akshara in enumerate(new_line['aksharas']):
                        new_units.append(TeluguUnit(
                            text=akshara,
                            start=orig_line.start + j * unit_duration,
                            end=orig_line.start + (j + 1) * unit_duration,
                            midi=None,
                            note_name=None,
                            confidence=None
                        ))
                
                aligned_new_lines.append(AlignedLine(
                    text=new_line['text'],
                    start=orig_line.start,
                    end=orig_line.end,
                    units=new_units,
                    unit_count=len(new_units),
                    line_index=i,
                    phrase_index=orig_line.phrase_index
                ))
            
            comp_time = (time.time() - comp_start) * 1000
            print(f"[PERF] New lyrics comparison & mapping: {comp_time:.2f} ms")
            
            total_time = (time.time() - total_start) * 1000
            print(f"[PERF] New lyrics alignment TOTAL: {total_time:.2f} ms")
            
            return AlignedLyrics(
                original_text=original_alignment.text,
                new_text=new_lyrics,
                lines=aligned_new_lines,
                comparisons=comparisons,
                total_units=sum(line.unit_count for line in aligned_new_lines),
                line_count=len(aligned_new_lines),
                metadata={
                    'original_line_count': original_alignment.line_count,
                    'original_total_units': original_alignment.total_units
                }
            )
            
        except Exception as e:
            raise LyricsAlignmentError(f"Failed to align new lyrics: {e}")
    
    def process_alignment(
        self,
        original_lyrics: str,
        new_lyrics: str,
        melody_path: str
    ) -> LyricsAlignmentResult:
        """
        Process full lyrics alignment (original + new).
        
        Args:
            original_lyrics: Original Telugu lyrics
            new_lyrics: New Telugu lyrics
            melody_path: Path to melody.json
            
        Returns:
            LyricsAlignmentResult
            
        Raises:
            LyricsAlignmentError: If alignment fails
        """
        try:
            original_alignment = self.align_original_lyrics(original_lyrics, melody_path)
            aligned_lyrics = self.align_new_lyrics(original_alignment, new_lyrics)
            
            return LyricsAlignmentResult(
                original_alignment=original_alignment,
                aligned_lyrics=aligned_lyrics,
                success=True,
                message="Alignment completed successfully"
            )
        except Exception as e:
            return LyricsAlignmentResult(
                original_alignment=None,
                aligned_lyrics=None,
                success=False,
                message=f"Alignment failed: {str(e)}"
            )


# Singleton instance
lyrics_alignment_service = LyricsAlignmentService()
