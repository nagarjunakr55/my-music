import os
import ssl
import numpy as np
import soundfile as sf
from app.services.stem_separation.base import StemSeparationService, StemSeparationResult, StemSeparationError


class DemucsMLXStemSeparationService(StemSeparationService):
    """Stem separation service using demucs-mlx for Apple Silicon."""
    
    def __init__(self, model: str = "htdemucs"):
        """
        Initialize the demucs-mlx separator.
        
        Args:
            model: Model name to use (default: htdemucs)
                   Options: htdemucs, htdemucs_ft, htdemucs_6s, hdemucs_mmi, mdx, mdx_extra
        """
        self.model = model
        self._separator = None
        # Bypass SSL verification for model download (development only)
        ssl._create_default_https_context = ssl._create_unverified_context
        self._load_separator()
    
    def _load_separator(self):
        """Load the demucs-mlx separator."""
        try:
            from demucs_mlx import Separator
            self._separator = Separator(model=self.model)
        except ImportError:
            raise StemSeparationError(
                "demucs-mlx is not installed. "
                "Install it with: pip install 'demucs-mlx[convert]'"
            )
        except Exception as e:
            raise StemSeparationError(f"Failed to load demucs-mlx separator: {e}")
    
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
        if not os.path.exists(input_file):
            raise StemSeparationError(f"Input file not found: {input_file}")
        
        if not os.path.exists(output_directory):
            os.makedirs(output_directory, exist_ok=True)
        
        try:
            # Perform separation
            origin, stems = self._separator.separate_audio_file(input_file)
            
            # stems is a dict: {"drums": array, "bass": array, "other": array, "vocals": array}
            if "vocals" not in stems:
                raise StemSeparationError("Vocals stem not found in separation result")
            
            # Extract vocals
            vocals_audio = stems["vocals"]
            
            # Create instrumental by mixing drums, bass, and other
            instrumental_audio = np.zeros_like(vocals_audio)
            for stem_name in ["drums", "bass", "other"]:
                if stem_name in stems:
                    instrumental_audio += stems[stem_name]
            
            # Save vocals
            vocals_path = os.path.join(output_directory, "vocals.wav")
            self._save_audio(vocals_audio, vocals_path)
            
            # Save instrumental
            instrumental_path = os.path.join(output_directory, "instrumental.wav")
            self._save_audio(instrumental_audio, instrumental_path)
            
            return StemSeparationResult(vocals_path=vocals_path, instrumental_path=instrumental_path)
            
        except Exception as e:
            raise StemSeparationError(f"Stem separation failed: {e}")
    
    def _save_audio(self, audio: np.ndarray, output_path: str, sample_rate: int = 44100):
        """
        Save audio array to WAV file.
        
        Args:
            audio: Audio array (channels, samples)
            output_path: Path to save the audio file
            sample_rate: Sample rate for the output file
        """
        # Transpose from (channels, samples) to (samples, channels) for soundfile
        if audio.ndim == 2:
            audio = audio.T
        elif audio.ndim == 1:
            audio = audio.reshape(-1, 1)
        
        sf.write(output_path, audio, sample_rate)


# Singleton instance
def get_stem_separation_service(model: str = "htdemucs") -> StemSeparationService:
    """Get a stem separation service instance."""
    return DemucsMLXStemSeparationService(model=model)
