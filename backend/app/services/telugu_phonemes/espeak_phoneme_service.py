import subprocess
from typing import List, Tuple
import re


class TeluguPhonemeError(Exception):
    """Custom exception for Telugu phoneme conversion errors."""
    pass


class TeluguPhonemeService:
    """Service for converting Telugu text to phonemes using espeak-ng."""
    
    def __init__(self, language: str = "te"):
        """
        Initialize the Telugu phoneme service.
        
        Args:
            language: Language code for espeak-ng (default: "te" for Telugu)
        """
        self.language = language
        self._validate_espeak_available()
    
    def _validate_espeak_available(self):
        """Check if espeak-ng is available on the system."""
        try:
            result = subprocess.run(
                ["espeak-ng", "--version"],
                capture_output=True,
                text=True,
                check=True
            )
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            raise TeluguPhonemeError(
                "espeak-ng is not installed or not available. "
                "Install it with: brew install espeak-ng (macOS) or apt install espeak-ng (Linux)"
            ) from e
    
    def text_to_phonemes(self, text: str) -> str:
        """
        Convert Telugu text to IPA phonemes using espeak-ng.
        
        Args:
            text: Telugu text to convert
            
        Returns:
            IPA phoneme string (space-separated phonemes)
            
        Raises:
            TeluguPhonemeError: If conversion fails
        """
        if not text or not text.strip():
            return ""
        
        try:
            # Call espeak-ng with IPA output
            result = subprocess.run(
                [
                    "espeak-ng",
                    f"-v{self.language}",
                    "-q",  # quiet mode
                    "--ipa",  # IPA output
                    text
                ],
                capture_output=True,
                text=True,
                check=True
            )
            
            phonemes = result.stdout.strip()
            
            # Clean up the output
            phonemes = self._clean_phonemes(phonemes)
            
            return phonemes
            
        except subprocess.CalledProcessError as e:
            raise TeluguPhonemeError(
                f"espeak-ng failed to convert text to phonemes: {e.stderr}"
            ) from e
    
    def text_to_phoneme_list(self, text: str) -> List[str]:
        """
        Convert Telugu text to a list of individual phonemes.
        
        Args:
            text: Telugu text to convert
            
        Returns:
            List of individual phoneme strings
            
        Raises:
            TeluguPhonemeError: If conversion fails
        """
        phonemes_str = self.text_to_phonemes(text)
        
        if not phonemes_str:
            return []
        
        # Split by spaces and filter empty strings
        phonemes = [p for p in phonemes_str.split() if p]
        
        return phonemes
    
    def akshara_to_phonemes(self, akshara: str) -> List[str]:
        """
        Convert a single Telugu akshara (syllable) to phonemes.
        
        Args:
            akshara: Single Telugu akshara
            
        Returns:
            List of phonemes for this akshara
            
        Raises:
            TeluguPhonemeError: If conversion fails
        """
        if not akshara or not akshara.strip():
            return []
        
        return self.text_to_phoneme_list(akshara)
    
    def _clean_phonemes(self, phonemes: str) -> str:
        """
        Clean up espeak-ng IPA output.
        
        Removes stress markers, extra spaces, and normalizes.
        
        Args:
            phonemes: Raw IPA output from espeak-ng
            
        Returns:
            Cleaned phoneme string
        """
        # Remove stress markers (ˈ, ˌ) - optional, keeping for now as they may be useful
        # phonemes = re.sub(r'[ˈˌ]', '', phonemes)
        
        # Normalize multiple spaces to single space
        phonemes = re.sub(r'\s+', ' ', phonemes)
        
        # Strip leading/trailing whitespace
        phonemes = phonemes.strip()
        
        return phonemes
    
    def batch_convert(self, texts: List[str]) -> List[str]:
        """
        Convert multiple Telugu texts to phonemes in batch.
        
        Args:
            texts: List of Telugu texts to convert
            
        Returns:
            List of phoneme strings (same order as input)
            
        Raises:
            TeluguPhonemeError: If any conversion fails
        """
        results = []
        for text in texts:
            phonemes = self.text_to_phonemes(text)
            results.append(phonemes)
        return results


# Singleton instance
telugu_phoneme_service = TeluguPhonemeService()
