import subprocess
import json
import os
from typing import Optional, Dict, Any
from pathlib import Path


class AudioProcessingError(Exception):
    """Custom exception for audio processing errors."""
    pass


class AudioProcessingService:
    """Service for audio processing using FFmpeg."""
    
    def __init__(self):
        self._check_ffmpeg()
    
    def _check_ffmpeg(self):
        """Verify FFmpeg is installed and accessible."""
        try:
            result = subprocess.run(
                ['ffmpeg', '-version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                raise AudioProcessingError("FFmpeg is not installed or not accessible")
        except FileNotFoundError:
            raise AudioProcessingError("FFmpeg is not installed. Please install FFmpeg.")
        except subprocess.TimeoutExpired:
            raise AudioProcessingError("FFmpeg command timed out")
    
    def probe_audio(self, file_path: str) -> Dict[str, Any]:
        """
        Probe audio file using ffprobe to get metadata.
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            Dictionary containing audio metadata (duration, sample rate, channels, etc.)
            
        Raises:
            AudioProcessingError: If probing fails
        """
        if not os.path.exists(file_path):
            raise AudioProcessingError(f"File not found: {file_path}")
        
        try:
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                file_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                raise AudioProcessingError(f"ffprobe failed: {result.stderr}")
            
            data = json.loads(result.stdout)
            
            # Extract relevant audio information
            format_info = data.get('format', {})
            streams = data.get('streams', [])
            audio_stream = next((s for s in streams if s.get('codec_type') == 'audio'), None)
            
            if not audio_stream:
                raise AudioProcessingError("No audio stream found in file")
            
            return {
                'duration': float(format_info.get('duration', 0)),
                'size': int(format_info.get('size', 0)),
                'bit_rate': int(format_info.get('bit_rate', 0)),
                'sample_rate': int(audio_stream.get('sample_rate', 0)),
                'channels': int(audio_stream.get('channels', 0)),
                'codec': audio_stream.get('codec_name', 'unknown'),
                'format': format_info.get('format_name', 'unknown')
            }
            
        except json.JSONDecodeError as e:
            raise AudioProcessingError(f"Failed to parse ffprobe output: {e}")
        except subprocess.TimeoutExpired:
            raise AudioProcessingError("ffprobe command timed out")
        except Exception as e:
            raise AudioProcessingError(f"Error probing audio: {e}")
    
    def validate_audio(self, file_path: str) -> bool:
        """
        Validate that the file is a valid audio file.
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            True if valid, raises AudioProcessingError otherwise
        """
        try:
            metadata = self.probe_audio(file_path)
            
            # Check if duration is reasonable (at least 0.1 seconds)
            if metadata['duration'] < 0.1:
                raise AudioProcessingError("Audio duration is too short")
            
            # Check if sample rate is reasonable
            if metadata['sample_rate'] < 8000 or metadata['sample_rate'] > 192000:
                raise AudioProcessingError(f"Invalid sample rate: {metadata['sample_rate']}")
            
            # Check if channels are reasonable
            if metadata['channels'] < 1 or metadata['channels'] > 8:
                raise AudioProcessingError(f"Invalid channel count: {metadata['channels']}")
            
            return True
            
        except AudioProcessingError:
            raise
        except Exception as e:
            raise AudioProcessingError(f"Validation failed: {e}")
    
    def get_duration(self, file_path: str) -> float:
        """
        Get the duration of an audio file in seconds.
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            Duration in seconds
        """
        metadata = self.probe_audio(file_path)
        return metadata['duration']
    
    def convert_to_wav(
        self,
        input_path: str,
        output_path: str,
        sample_rate: int = 44100,
        channels: int = 2,
        bitrate: str = '192k'
    ) -> None:
        """
        Convert audio file to WAV format with specified parameters.
        
        Args:
            input_path: Path to input audio file
            output_path: Path for output WAV file
            sample_rate: Target sample rate (default: 44100 Hz)
            channels: Target channel count (default: 2 for stereo)
            bitrate: Target bitrate (default: 192k)
            
        Raises:
            AudioProcessingError: If conversion fails
        """
        if not os.path.exists(input_path):
            raise AudioProcessingError(f"Input file not found: {input_path}")
        
        # Ensure output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        try:
            cmd = [
                'ffmpeg',
                '-i', input_path,
                '-ar', str(sample_rate),
                '-ac', str(channels),
                '-b:a', bitrate,
                '-acodec', 'pcm_s16le',  # 16-bit PCM
                '-y',  # Overwrite output file if exists
                output_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout for conversion
            )
            
            if result.returncode != 0:
                raise AudioProcessingError(f"FFmpeg conversion failed: {result.stderr}")
            
            if not os.path.exists(output_path):
                raise AudioProcessingError("Output file was not created")
            
            # Validate the output
            self.validate_audio(output_path)
            
        except subprocess.TimeoutExpired:
            raise AudioProcessingError("FFmpeg conversion timed out")
        except Exception as e:
            raise AudioProcessingError(f"Error converting to WAV: {e}")
    
    def normalize_audio(
        self,
        input_path: str,
        output_path: str,
        target_sample_rate: int = 44100,
        target_channels: int = 2
    ) -> None:
        """
        Normalize audio to a standard format suitable for stem separation.
        
        This converts to WAV with consistent sample rate, channels, and bit depth.
        
        Args:
            input_path: Path to input audio file
            output_path: Path for normalized WAV file
            target_sample_rate: Target sample rate (default: 44100 Hz)
            target_channels: Target channel count (default: 2 for stereo)
            
        Raises:
            AudioProcessingError: If normalization fails
        """
        self.convert_to_wav(
            input_path,
            output_path,
            sample_rate=target_sample_rate,
            channels=target_channels,
            bitrate='192k'
        )
    
    def prepare_for_transcription(
        self,
        input_path: str,
        output_path: str,
        sample_rate: int = 16000,
        channels: int = 1
    ) -> None:
        """
        Prepare audio for transcription by converting to mono and 16kHz.
        
        Whisper models work best with mono 16kHz audio. This creates a
        transcription-optimized version without modifying the original.
        
        Args:
            input_path: Path to input audio file (e.g., vocals.wav)
            output_path: Path for transcription-optimized audio
            sample_rate: Target sample rate (default: 16000 Hz for Whisper)
            channels: Target channel count (default: 1 for mono)
            
        Raises:
            AudioProcessingError: If preparation fails
        """
        if not os.path.exists(input_path):
            raise AudioProcessingError(f"Input file not found: {input_path}")
        
        # Ensure output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        try:
            cmd = [
                'ffmpeg',
                '-i', input_path,
                '-ar', str(sample_rate),
                '-ac', str(channels),
                '-acodec', 'pcm_s16le',  # 16-bit PCM
                '-y',  # Overwrite output file if exists
                output_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode != 0:
                raise AudioProcessingError(f"FFmpeg transcription preparation failed: {result.stderr}")
            
            if not os.path.exists(output_path):
                raise AudioProcessingError("Output file was not created")
            
            # Validate the output
            self.validate_audio(output_path)
            
        except subprocess.TimeoutExpired:
            raise AudioProcessingError("FFmpeg transcription preparation timed out")
        except Exception as e:
            raise AudioProcessingError(f"Error preparing audio for transcription: {e}")


# Singleton instance
audio_processor = AudioProcessingService()
