#!/usr/bin/env python3
"""Transform Telugu TTS speech into singing-like vocals using librosa."""

import json
import numpy as np
import soundfile as sf
import librosa
import time

def midi_to_hz(midi_note):
    """Convert MIDI note number to frequency in Hz."""
    return 440.0 * (2.0 ** ((midi_note - 69) / 12.0))

def main():
    print("=" * 60)
    print("Pitch/Time Transformation Test (Librosa PSOLA-like)")
    print("=" * 60)
    
    # Load TTS speech
    print("\nLoading test_telugu_speech.wav...")
    audio, sr = sf.read("test_telugu_speech.wav")
    print(f"Sample rate: {sr} Hz")
    print(f"Duration: {len(audio) / sr:.2f} seconds")
    print(f"Audio shape: {audio.shape}")
    
    # Load aligned lyrics
    print("\nLoading aligned_lyrics.json...")
    with open("backend/data/jobs/04b49fae-0002-4a73-a8f4-37c3c8f78c0d/analysis/aligned_lyrics.json", 'r') as f:
        aligned_lyrics = json.load(f)
    
    # Extract first line (our test phrase: నా చూపులే నీ ఊపిరై)
    first_line = aligned_lyrics["lines"][0]
    print(f"Test phrase: {first_line['text']}")
    print(f"Number of units: {first_line['unit_count']}")
    
    # Extract non-space units (actual syllables)
    syllables = [u for u in first_line["units"] if u["text"].strip()]
    print(f"Number of syllables: {len(syllables)}")
    
    # The aligned_lyrics timestamps are from the original song (starting at 22s)
    # We need to remap them to fit within our TTS audio duration
    line_start = first_line["start"]
    line_end = first_line["end"]
    line_duration = line_end - line_start
    
    print(f"Original line timing: {line_start:.2f}s to {line_end:.2f}s (duration: {line_duration:.2f}s)")
    print(f"TTS audio duration: {len(audio) / sr:.2f}s")
    
    # Remap syllable timing to fit TTS duration
    tts_duration = len(audio) / sr
    for syl in syllables:
        # Normalize to 0-1 range within the line
        norm_start = (syl["start"] - line_start) / line_duration
        norm_end = (syl["end"] - line_start) / line_duration
        
        # Scale to TTS duration
        syl["remapped_start"] = norm_start * tts_duration
        syl["remapped_end"] = norm_end * tts_duration
        
        print(f"  {syl['text']} - MIDI {syl['midi']} ({midi_to_hz(syl['midi']):.1f} Hz) - {syl['remapped_start']:.2f}s to {syl['remapped_end']:.2f}s")
    
    # Get current pitch of TTS speech
    print("\nAnalyzing current pitch...")
    analysis_start = time.time()
    
    # Convert to float32 for librosa
    audio_float32 = audio.astype(np.float32)
    
    # Extract pitch using librosa
    f0, voiced_flag, voiced_probs = librosa.pyin(
        audio_float32,
        sr=sr,
        fmin=librosa.note_to_hz('C2'),
        fmax=librosa.note_to_hz('C7'),
        frame_length=2048,
        hop_length=512
    )
    
    analysis_time = time.time() - analysis_start
    print(f"Pitch analysis completed in {analysis_time:.2f} seconds")
    print(f"F0 frames: {len(f0)}")
    
    # Calculate average pitch of TTS
    avg_f0 = f0[voiced_flag].mean()
    print(f"Average TTS pitch: {avg_f0:.1f} Hz")
    
    # Process each syllable with pitch shifting
    print("\nProcessing syllables with pitch shifting...")
    transform_start = time.time()
    
    # Resample to target sample rate if needed (librosa prefers 22050)
    target_sr = 22050
    if sr != target_sr:
        audio_float32 = librosa.resample(audio_float32, orig_sr=sr, target_sr=target_sr)
        sr = target_sr
        print(f"Resampled to {sr} Hz")
    
    # Create output audio buffer
    output_audio = np.zeros_like(audio_float32)
    
    for i, syl in enumerate(syllables):
        start_time = syl["remapped_start"]
        end_time = syl["remapped_end"]
        target_midi = syl["midi"]
        target_hz = midi_to_hz(target_midi)
        
        # Convert time to samples
        start_sample = int(start_time * sr)
        end_sample = int(end_time * sr)
        
        # Clamp to valid range
        start_sample = max(0, start_sample)
        end_sample = min(len(audio_float32), end_sample)
        
        if start_sample >= end_sample:
            continue
        
        # Extract syllable audio
        syllable_audio = audio_float32[start_sample:end_sample]
        
        # Calculate pitch shift ratio
        # Use average TTS pitch as reference
        pitch_shift_ratio = target_hz / avg_f0
        
        # Pitch shift the syllable
        shifted_syllable = librosa.effects.pitch_shift(
            syllable_audio,
            sr=sr,
            n_steps=pitch_shift_ratio
        )
        
        # Place in output (simple placement, no time stretching yet)
        output_start = start_sample
        output_end = min(output_start + len(shifted_syllable), len(output_audio))
        
        if output_start < output_end:
            output_audio[output_start:output_end] = shifted_syllable[:output_end-output_start]
        
        print(f"  '{syl['text']}' - Pitch shift: {pitch_shift_ratio:.2f}x ({avg_f0:.1f} -> {target_hz:.1f} Hz)")
    
    transform_time = time.time() - transform_start
    print(f"Transformation completed in {transform_time:.2f} seconds")
    
    # Save output
    output_path = "test_telugu_vocal.wav"
    sf.write(output_path, output_audio.astype(np.float32), sr)
    print(f"\nAudio saved to: {output_path}")
    print(f"Duration: {len(output_audio) / sr:.2f} seconds")
    
    print("\n" + "=" * 60)
    print("Test completed successfully!")
    print("=" * 60)
    
    print("\nNote: This is a basic pitch-shifting approach using librosa.")
    print("Formant preservation is limited (librosa pitch_shift preserves formants reasonably).")
    print("Timing adjustment not implemented (syllables placed at original TTS timing).")

if __name__ == "__main__":
    main()
