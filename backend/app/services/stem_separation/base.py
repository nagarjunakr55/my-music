from abc import ABC, abstractmethod
from typing import Dict
from pathlib import Path


class StemSeparationResult:
    """Result of stem separation operation."""
    
    def __init__(self, vocals_path: str, instrumental_path: str):
        self.vocals_path = vocals_path
        self.instrumental_path = instrumental_path


class StemSeparationService(ABC):
    """Abstract base class for stem separation services."""
    
    @abstractmethod
    def separate(self, input_file: str, output_directory: str) -> StemSeparationResult:
        """
        Separate audio file into vocals and instrumental stems.
        
        Args:
            input_file: Path to input audio file (WAV format recommended)
            output_directory: Directory where stem files will be saved
            
        Returns:
            StemSeparationResult containing paths to vocals and instrumental files
            
        Raises:
            StemSeparationError: If separation fails
        """
        pass


class StemSeparationError(Exception):
    """Custom exception for stem separation errors."""
    pass
