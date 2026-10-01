import asyncio
import os
import json
from app.jobs.job_manager import job_manager
from app.models.job import JobStatus, ProcessingStage
from app.services.audio_processing import audio_processor, AudioProcessingError
from app.services.stem_separation import get_stem_separation_service, StemSeparationError
from app.services.vocal_analysis import get_vocal_analysis_service, VocalAnalysisError
from app.services.lyrics_transcription import get_lyrics_transcription_service, LyricsTranscriptionError


async def process_job_real(job_id: str, original_path: str, job_dir: str):
    """Real processing pipeline with audio normalization, stem separation, melody analysis, and lyrics transcription."""
    
    try:
        # Stage 1: Upload complete
        job_manager.update_job(job_id, JobStatus.PROCESSING, ProcessingStage.UPLOAD_COMPLETE, 5)
        
        # Stage 2: Normalize audio
        job_manager.update_job(job_id, JobStatus.PROCESSING, ProcessingStage.NORMALIZING_AUDIO, 10)
        
        normalized_path = os.path.join(job_dir, "normalized.wav")
        
        try:
            # Validate the uploaded audio
            audio_processor.validate_audio(original_path)
            
            # Convert to normalized WAV
            audio_processor.normalize_audio(
                original_path,
                normalized_path,
                target_sample_rate=44100,
                target_channels=2
            )
            
            job_manager.update_job(job_id, JobStatus.PROCESSING, ProcessingStage.NORMALIZING_AUDIO, 20)
            
        except AudioProcessingError as e:
            job_manager.update_job(job_id, JobStatus.FAILED, error=f"Audio normalization failed: {e}")
            return
        
        # Stage 3: Real stem separation using demucs-mlx
        job_manager.update_job(job_id, JobStatus.PROCESSING, ProcessingStage.SEPARATING_VOCALS, 25)
        
        try:
            # Get stem separation service
            stem_service = get_stem_separation_service(model="htdemucs")
            
            # Perform stem separation
            result = stem_service.separate(normalized_path, job_dir)
            
            job_manager.update_job(job_id, JobStatus.PROCESSING, ProcessingStage.SEPARATING_VOCALS, 50)
            job_manager.update_job(job_id, JobStatus.PROCESSING, ProcessingStage.STEMS_READY, 55)
            
        except StemSeparationError as e:
            job_manager.update_job(job_id, JobStatus.FAILED, error=f"Stem separation failed: {e}")
            return
        except Exception as e:
            job_manager.update_job(job_id, JobStatus.FAILED, error=f"Stem separation error: {str(e)}")
            return
        
        # Stage 4: Real melody analysis using librosa
        job_manager.update_job(job_id, JobStatus.PROCESSING, ProcessingStage.ANALYZING_MELODY, 60)
        
        try:
            # Get vocal analysis service
            vocal_service = get_vocal_analysis_service()
            
            # Perform melody analysis on vocals
            vocals_path = os.path.join(job_dir, "vocals.wav")
            analysis_result = vocal_service.analyze(vocals_path)
            
            # Create analysis directory
            analysis_dir = os.path.join(job_dir, "analysis")
            os.makedirs(analysis_dir, exist_ok=True)
            
            # Save melody.json
            melody_path = os.path.join(analysis_dir, "melody.json")
            with open(melody_path, 'w') as f:
                json.dump(analysis_result.model_dump(), f, indent=2)
            
            job_manager.update_job(job_id, JobStatus.PROCESSING, ProcessingStage.ANALYZING_MELODY, 70)
            
        except VocalAnalysisError as e:
            job_manager.update_job(job_id, JobStatus.FAILED, error=f"Melody analysis failed: {e}")
            return
        except Exception as e:
            job_manager.update_job(job_id, JobStatus.FAILED, error=f"Melody analysis error: {str(e)}")
            return
        
        # Stage 5: Real lyrics transcription using OpenAI Whisper (OPTIONAL/EXPERIMENTAL)
        # Only run if WHISPER_ENABLED environment variable is set to "true"
        # This saves processing time since the main workflow expects user-provided lyrics
        if os.getenv("WHISPER_ENABLED", "false").lower() == "true":
            job_manager.update_job(job_id, JobStatus.PROCESSING, ProcessingStage.ALIGNING_LYRICS, 75)
            
            try:
                # Get OpenAI Whisper transcription service
                lyrics_service = get_lyrics_transcription_service(
                    model_size="small",  # Use small model for better accuracy
                    device="cpu",
                    language=None  # Auto-detect language
                )
                
                # Perform lyrics transcription on vocals
                transcription_result = lyrics_service.transcribe(vocals_path)
                
                # Save lyrics.json
                lyrics_path = os.path.join(analysis_dir, "lyrics.json")
                with open(lyrics_path, 'w') as f:
                    json.dump(transcription_result.model_dump(), f, indent=2)
                
                job_manager.update_job(job_id, JobStatus.PROCESSING, ProcessingStage.ALIGNING_LYRICS, 80)
                
            except LyricsTranscriptionError as e:
                # Don't fail the job if transcription fails - it's optional
                print(f"Lyrics transcription failed (optional): {e}")
            except Exception as e:
                # Don't fail the job if transcription fails - it's optional
                print(f"Lyrics transcription error (optional): {str(e)}")
        else:
            # Skip transcription - user will provide lyrics
            job_manager.update_job(job_id, JobStatus.PROCESSING, ProcessingStage.ALIGNING_LYRICS, 80)
        
        # Continue with mock stages for the rest of the pipeline
        # These will be implemented in later phases
        stages = [
            (ProcessingStage.GENERATING_VOCALS, 90),
            (ProcessingStage.MIXING, 95),
            (ProcessingStage.FINALIZING, 98),
            (ProcessingStage.COMPLETED, 100),
        ]
        
        for stage, progress in stages:
            await asyncio.sleep(1)
            job_manager.update_job(job_id, JobStatus.PROCESSING, stage, progress)
        
        job_manager.update_job(job_id, JobStatus.COMPLETED, ProcessingStage.COMPLETED, 100)
        
    except Exception as e:
        job_manager.update_job(job_id, JobStatus.FAILED, error=f"Processing failed: {str(e)}")
