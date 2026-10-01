from typing import List, Dict, Any
from akshara_tokenizer import segment_aksharas, count_aksharas


class TeluguSegmentationError(Exception):
    """Custom exception for Telugu segmentation errors."""
    pass


class TeluguLyricsSegmentationService:
    """Service for segmenting Telugu lyrics into linguistically correct aksharas (graphemes)."""
    
    def __init__(self):
        """Initialize the Telugu segmentation service."""
        pass
    
    def segment_text(self, text: str) -> List[str]:
        """
        Segment Telugu text into aksharas (orthographic syllables).
        
        This uses akshara-tokenizer which correctly handles:
        - Consonant clusters (conjuncts)
        - Vowel signs (matras)
        - Virama (halant)
        - Anusvara, visarga
        - Dependent vowels
        - Independent vowels
        
        Args:
            text: Telugu text to segment
            
        Returns:
            List of akshara strings
            
        Raises:
            TeluguSegmentationError: If segmentation fails
        """
        try:
            # Use akshara-tokenizer's segment_aksharas function
            aksharas = segment_aksharas(text)
            return aksharas
        except Exception as e:
            raise TeluguSegmentationError(f"Failed to segment Telugu text: {e}")
    
    def count_aksharas(self, text: str) -> int:
        """
        Count the number of aksharas in Telugu text.
        
        Args:
            text: Telugu text
            
        Returns:
            Number of aksharas
        """
        try:
            return count_aksharas(text)
        except Exception as e:
            raise TeluguSegmentationError(f"Failed to count aksharas: {e}")
    
    def segment_lyrics_with_structure(self, lyrics: str) -> Dict[str, Any]:
        """
        Segment lyrics while preserving line structure.
        
        Args:
            lyrics: Multi-line Telugu lyrics
            
        Returns:
            Dictionary containing:
            - lines: List of line dictionaries with:
                - text: Original line text
                - aksharas: List of aksharas in the line
                - count: Number of aksharas
            - total_aksharas: Total number of aksharas across all lines
            - line_count: Number of lines
            
        Raises:
            TeluguSegmentationError: If segmentation fails
        """
        try:
            lines = lyrics.strip().split('\n')
            result_lines = []
            total_aksharas = 0
            
            for line in lines:
                line = line.strip()
                if not line:
                    # Preserve empty lines
                    result_lines.append({
                        'text': '',
                        'aksharas': [],
                        'count': 0
                    })
                    continue
                
                aksharas = self.segment_text(line)
                count = len(aksharas)
                total_aksharas += count
                
                result_lines.append({
                    'text': line,
                    'aksharas': aksharas,
                    'count': count
                })
            
            return {
                'lines': result_lines,
                'total_aksharas': total_aksharas,
                'line_count': len(lines)
            }
        except Exception as e:
            raise TeluguSegmentationError(f"Failed to segment lyrics with structure: {e}")


# Singleton instance
telugu_segmentation_service = TeluguLyricsSegmentationService()
