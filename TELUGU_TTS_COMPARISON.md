# Telugu TTS Comparison Report

## Executive Summary

**Recommended: Chatterbox-Telugu** for POC

- High-quality Telugu pronunciation
- Apple Silicon compatible (MPS)
- Permissive license (CC-BY-4.0, commercial use permitted)
- Simple Python API
- Fast inference
- No server required

---

## Telugu TTS Options Investigated

### 1. Chatterbox-Telugu

**Repository**: https://huggingface.co/shankarpandala/chatterbox-telugu

**License**: CC-BY-4.0 (attribution required, commercial use permitted)

**Telugu Support**: ✅ Native Telugu + code-switching (Telugu + English)

**Voice Quality**: High-quality (based on Resemble AI Chatterbox)

**Local/Cloud**: Local (Hugging Face)

**Apple Silicon Compatibility**: ✅ Yes (MPS support explicitly mentioned)

**Inference Speed**: Fast (Chatterbox T3 ~0.5B model)

**Word/Phoneme Timing**: ❌ Not directly available (end-to-end model)

**Rate/Prosody Controls**: ✅ Yes (via generation parameters)

**Model Size**: ~0.5B parameters (reasonable)

**Installation**: Simple (pip install chatterbox-tts)

**Code Example**:
```python
from chatterbox.mtl_tts import ChatterboxMultilingualTTS
from huggingface_hub import snapshot_download

ckpt = snapshot_download("shankarpandala/chatterbox-telugu")
model = ChatterboxMultilingualTTS.from_local(ckpt, device="mps")

wav = model.generate(
    "నా చూపులే నీ ఊపిరై",
    language_id="te",
    audio_prompt_path="reference.wav"  # Optional for voice cloning
)
```

**Pros**:
- High-quality Telugu pronunciation
- Apple Silicon native support
- Simple API
- Code-switching support
- Voice cloning capability
- Permissive license

**Cons**:
- Requires reference audio for voice cloning (optional)
- No direct phoneme-level timing output

---

### 2. Praxy Voice R6

**Repository**: https://huggingface.co/Praxel/praxy-voice-r6

**License**: Apache-2.0 (adapter), MIT (base Chatterbox)

**Telugu Support**: ✅ Telugu (via LoRA adapter on Chatterbox)

**Voice Quality**: High-quality (LoRA fine-tune on Chatterbox)

**Local/Cloud**: Local (Hugging Face)

**Apple Silicon Compatibility**: ✅ Yes (MPS support)

**Inference Speed**: Fast (Chatterbox base + LoRA)

**Word/Phoneme Timing**: ❌ Not directly available

**Rate/Prosody Controls**: ✅ Yes (exaggeration, temperature, min_p parameters)

**Model Size**: Base Chatterbox + LoRA adapter

**Installation**: Moderate (requires Chatterbox + PEFT + indic-transliteration)

**Code Example**:
```python
from chatterbox.mtl_tts import ChatterboxMultilingualTTS
from peft import LoraConfig, get_peft_model
from huggingface_hub import hf_hub_download
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate

# Load base model + LoRA
model = ChatterboxMultilingualTTS.from_pretrained(device="mps")
# ... LoRA setup ...

# BUPS romanisation required
text = "నా చూపులే నీ ఊపిరై"
text_roman = transliterate(text, sanscript.TELUGU, sanscript.ISO)

wav = model.generate(text_roman, language_id="hi", audio_prompt_path="ref.wav")
```

**Pros**:
- High-quality Telugu pronunciation
- Apple Silicon support
- Permissive license (Apache-2.0)
- Fine-tuned specifically for Telugu

**Cons**:
- More complex setup (requires LoRA, BUPS romanisation)
- Requires reference audio for voice cloning
- Uses Hindi proxy for Telugu (workaround)
- No direct phoneme-level timing

---

### 3. Facebook MMS-TTS (Telugu)

**Repository**: https://huggingface.co/facebook/mms-tts-tel

**License**: CC-BY-NC 4.0 (non-commercial)

**Telugu Support**: ✅ Native Telugu

**Voice Quality**: Good (VITS-based)

**Local/Cloud**: Local (Hugging Face, Transformers)

**Apple Silicon Compatibility**: ✅ Yes (PyTorch MPS)

**Inference Speed**: Fast (VITS is efficient)

**Word/Phoneme Timing**: ❌ Not directly available

**Rate/Prosody Controls**: ❌ Limited (basic VITS controls)

**Model Size**: VITS checkpoint (moderate)

**Installation**: Simple (pip install transformers)

**Code Example**:
```python
from transformers import VitsModel, AutoTokenizer

model = VitsModel.from_pretrained("facebook/mms-tts-tel")
tokenizer = AutoTokenizer.from_pretrained("facebook/mms-tts-tel")

text = "నా చూపులే నీ ఊపిరై"
inputs = tokenizer(text, return_tensors="pt")

with torch.no_grad():
    output = model(**inputs).waveform
```

**Pros**:
- Simple installation
- Apple Silicon support
- Good quality
- Facebook/Meta maintained

**Cons**:
- Non-commercial license (CC-BY-NC 4.0)
- No voice cloning
- Limited prosody controls
- Older VITS architecture

---

### 4. VEXYL-TTS

**Repository**: https://github.com/vexyl-ai/vexyl-tts

**License**: Not specified (wraps ai4bharat/indic-parler-tts)

**Telugu Support**: ✅ Telugu (22 Indian languages)

**Voice Quality**: Good (Indic Parler TTS)

**Local/Cloud**: Local (self-hosted server)

**Apple Silicon Compatibility**: ✅ Yes (MPS support)

**Inference Speed**: Fast (REST/WebSocket API)

**Word/Phoneme Timing**: ❌ Not directly available

**Rate/Prosody Controls**: ✅ Yes (voice presets, tone/style control)

**Model Size**: ~6GB disk space

**Installation**: Complex (requires Docker, server setup)

**Speakers**: 44 speakers total (Telugu: Lalitha female, Prakash male)

**Pros**:
- Multiple speakers
- Voice presets with tone/style control
- Apple Silicon support
- Self-hosted (no API costs)

**Cons**:
- Complex setup (requires running server)
- ~6GB disk space
- License unclear
- Overkill for simple POC

---

### 5. F5-TTS-TELUGU

**Repository**: https://huggingface.co/CallWhiz/F5-TTS-TELUGU

**License**: CC-BY-NC 4.0 (non-commercial)

**Telugu Support**: ✅ Telugu (fine-tuned F5-TTS)

**Voice Quality**: Good (F5-TTS based)

**Local/Cloud**: Local (Hugging Face)

**Apple Silicon Compatibility**: Likely (PyTorch)

**Inference Speed**: Moderate (5.1GB model)

**Word/Phoneme Timing**: ❌ Not directly available

**Rate/Prosody Controls**: ✅ Yes (F5-TTS controls)

**Model Size**: 5.1GB (very large)

**Installation**: Moderate (requires F5-TTS setup)

**Pros**:
- Voice cloning capability
- Good quality

**Cons**:
- Non-commercial license
- Very large model (5.1GB)
- Slower inference due to size
- Overkill for POC

---

### 6. IndicTTSCustom (AI4Bharat)

**Repository**: https://github.com/ai4bharat/indic-tts

**License**: Not specified (open-sourced on Bhashini)

**Telugu Support**: ✅ Telugu (13 Indian languages)

**Voice Quality**: SOTA for Indian languages (FastPitch + HiFi-GAN)

**Local/Cloud**: Local (Coqui TTS)

**Apple Silicon Compatibility**: Likely (PyTorch)

**Inference Speed**: Fast (FastPitch + HiFi-GAN)

**Word/Phoneme Timing**: ❌ Not directly available

**Rate/Prosody Controls**: ✅ Yes (Coqui TTS controls)

**Model Size**: Moderate (FastPitch + HiFi-GAN)

**Installation**: Complex (requires Coqui TTS setup)

**Pros**:
- SOTA quality for Indian languages
- Research-backed (ICASSP 2023)
- FastPitch + HiFi-GAN architecture

**Cons**:
- Complex setup (Coqui TTS)
- License unclear
- Requires dataset formatting
- Overkill for simple POC

---

## Comparison Summary

| Model | License | Quality | Apple Silicon | Setup Complexity | Inference Speed | Commercial Use |
|-------|---------|---------|---------------|-----------------|----------------|----------------|
| Chatterbox-Telugu | CC-BY-4.0 | High | ✅ Yes | Simple | Fast | ✅ Yes |
| Praxy Voice R6 | Apache-2.0 | High | ✅ Yes | Moderate | Fast | ✅ Yes |
| MMS-TTS | CC-BY-NC 4.0 | Good | ✅ Yes | Simple | Fast | ❌ No |
| VEXYL-TTS | Unclear | Good | ✅ Yes | Complex | Fast | ? |
| F5-TTS-TELUGU | CC-BY-NC 4.0 | Good | Likely | Moderate | Moderate | ❌ No |
| IndicTTSCustom | Unclear | SOTA | Likely | Complex | Fast | ? |

---

## Recommendation

### **Chatterbox-Telugu** for POC

**Rationale**:
1. **High-quality Telugu pronunciation** - specifically fine-tuned for Telugu
2. **Apple Silicon native support** - explicit MPS support
3. **Permissive license** - CC-BY-4.0 allows commercial use with attribution
4. **Simple setup** - pip install, no server required
5. **Fast inference** - suitable for real-time processing
6. **Code-switching support** - handles Telugu + English if needed
7. **Voice cloning optional** - can use default voice or clone

**Next Steps**:
1. Install Chatterbox-Telugu
2. Generate test_telugu_speech.wav with phrase "నా చూపులే నీ ఊపిరై"
3. Verify Telugu pronunciation quality
4. If acceptable, proceed to pitch/time manipulation

---

## Alternative: Praxy Voice R6

If Chatterbox-Telugu has issues, Praxy Voice R6 is a strong alternative:
- Apache-2.0 license (more permissive)
- Similar quality
- Apple Silicon support
- More complex setup (LoRA + BUPS romanisation)

---

## Rejected Options

1. **MMS-TTS**: Non-commercial license (CC-BY-NC 4.0)
2. **F5-TTS-TELUGU**: Non-commercial license, very large model (5.1GB)
3. **VEXYL-TTS**: Complex setup, unclear license, overkill for POC
4. **IndicTTSCustom**: Complex setup, unclear license, overkill for POC

---

## Installation Plan for Chatterbox-Telugu

```bash
pip install chatterbox-tts huggingface-hub
```

```python
from chatterbox.mtl_tts import ChatterboxMultilingualTTS
from huggingface_hub import snapshot_download
import torch

# Download model
ckpt = snapshot_download("shankarpandala/chatterbox-telugu")

# Load model (Apple Silicon MPS)
model = ChatterboxMultilingualTTS.from_local(ckpt, device="mps")

# Generate speech
text = "నా చూపులే నీ ఊపిరై"
wav = model.generate(text, language_id="te")

# Save
import soundfile as sf
sf.write("test_telugu_speech.wav", wav.numpy(), model.sr)
```

---

## Next Phase: Audio Manipulation Research

After generating test_telugu_speech.wav, research pitch/time manipulation tools:
- WORLD vocoder
- Rubber Band
- librosa
- PSOLA
- Praat/parselmouth

Select approach that preserves formants while changing F0 and duration.
