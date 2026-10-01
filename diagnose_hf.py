#!/usr/bin/env python3
"""Diagnose Hugging Face download issues."""

import os
import sys

# Disable XET
os.environ['HF_HUB_DISABLE_XET'] = '1'
os.environ['HF_HUB_ENABLE_HF_TRANSFER'] = '0'

from huggingface_hub import hf_hub_download, snapshot_download

print("=" * 60)
print("Hugging Face Download Diagnosis")
print("=" * 60)

print(f"\nEnvironment:")
print(f"  HF_HUB_DISABLE_XET: {os.environ.get('HF_HUB_DISABLE_XET')}")
print(f"  HF_HUB_ENABLE_HF_TRANSFER: {os.environ.get('HF_HUB_ENABLE_HF_TRANSFER')}")

print(f"\nRepository Info:")
print(f"  Model: shankarpandala/chatterbox-telugu")
print(f"  Expected: Public, CC-BY-4.0")

print(f"\nInstalled Versions:")
import huggingface_hub
print(f"  huggingface_hub: {huggingface_hub.__version__}")

try:
    import hf_xet
    print(f"  hf_xet: installed (version unknown)")
except ImportError:
    print(f"  hf_xet: Not installed")

print("\n" + "=" * 60)
print("Test 1: Single file download with XET disabled")
print("=" * 60)

try:
    print("\nAttempting to download: config.json")
    file_path = hf_hub_download(
        repo_id="shankarpandala/chatterbox-telugu",
        filename="config.json",
        repo_type="model"
    )
    print(f"SUCCESS: {file_path}")
except Exception as e:
    print(f"FAILED: {type(e).__name__}: {e}")

print("\n" + "=" * 60)
print("Test 2: Snapshot download with XET disabled")
print("=" * 60)

try:
    print("\nAttempting snapshot download...")
    local_dir = snapshot_download(
        repo_id="shankarpandala/chatterbox-telugu",
        repo_type="model",
        local_dir="chatterbox-telugu-test"
    )
    print(f"SUCCESS: {local_dir}")
except Exception as e:
    print(f"FAILED: {type(e).__name__}: {e}")

print("\n" + "=" * 60)
print("Diagnosis Complete")
print("=" * 60)
