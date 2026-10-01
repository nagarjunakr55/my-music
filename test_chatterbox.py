#!/usr/bin/env python3
"""Test script for Telugu TTS generation using espeak-ng as fallback."""

import os
import subprocess
import time
import soundfile as sf

def main():
    print("=" * 60)
    print("espeak-ng Telugu Test (Fallback from Neural TTS)")
    print("=" * 60)
    
    # Check espeak-ng availability
    print("\nChecking espeak-ng...")
    try:
        result = subprocess.run(
            ["espeak-ng", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"espeak-ng available: {result.stdout.strip()}")
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print("ERROR: espeak-ng not available")
        return
    
    # Test phrase
    text = "నా చూపులే నీ ఊపిరై"
    print(f"\nGenerating speech for: '{text}'")
    print("Using espeak-ng with Telugu voice")
    print("Note: This is a rule-based TTS, not neural TTS")
    print("Quality will be lower than Chatterbox/MMS-TTS")
    
    # Generate speech
    print("\nGenerating speech...")
    gen_start = time.time()
    
    output_path = "test_telugu_speech.wav"
    result = subprocess.run(
        [
            "espeak-ng",
            "-v", "te",  # Telugu voice
            "-w", output_path,  # Output WAV file
            text
        ],
        capture_output=True,
        text=True,
        check=True
    )
    
    gen_time = time.time() - gen_start
    print(f"Speech generated in {gen_time:.2f} seconds")
    
    # Load and get audio info
    audio, sr = sf.read(output_path)
    print(f"\nAudio saved to: {output_path}")
    print(f"Sample rate: {sr} Hz")
    print(f"Duration: {len(audio) / sr:.2f} seconds")
    
    print("\n" + "=" * 60)
    print("Test completed successfully!")
    print("=" * 60)

if __name__ == "__main__":
    main()
