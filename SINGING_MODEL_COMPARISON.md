# Singing Model Comparison Report

## Executive Summary

**No pretrained Telugu singing synthesis model exists.** However, a viable path forward exists by combining:
- **espeak-ng** for Telugu phoneme conversion (available, supports Telugu script)
- **DiffSinger** with custom Telugu phoneme dictionary (supports custom phoneme sets, pitch control, duration control)
- **Our existing melody.json/aligned_lyrics.json** for pitch/timing constraints

This approach requires no model training and leverages mature, open-source components.

---

## Candidate Models Investigated

### 1. DiffSinger (OpenVPI maintained version)

**Repository**: https://github.com/openvpi/DiffSinger

**Last meaningful activity**: Active (2024 releases, ongoing maintenance)

**License**: Apache License 2.0

**Supported languages**: 
- Pretrained: Chinese, Japanese, English
- Custom: Any language via custom phoneme dictionary

**Telugu support**: 
- **No pretrained Telugu model**
- **Custom phoneme dictionary supported** - can add Telugu phonemes
- Universal dictionary system allows any phoneme set

**Custom phoneme support**: ✅ Excellent
- Universal dictionary and phoneme system support
- Can define custom phoneme sets for any language
- Language-specific phoneme prefixes supported
- Global phonemes (SP, AP) available

**Input format**:
- Phoneme sequence (customizable)
- Pitch (F0 curve)
- Note durations
- Phoneme durations
- Optional: energy, breathiness, tension

**Pitch supplied**: ✅ Yes
- F0 curve as input
- Variance models for pitch prediction/control
- Can override with supplied pitch

**Note duration supplied**: ✅ Yes
- Note durations as input
- Phoneme durations as input
- Duration predictor available

**Phoneme duration supplied**: ✅ Yes
- Explicit phoneme duration control
- Duration prediction available if not supplied

**Output format**: WAV (44.1kHz)

**Python version**: Python 3.8+

**macOS compatibility**: ✅ Yes

**Apple Silicon compatibility**: ✅ Yes (PyTorch MPS support)

**CPU support**: ✅ Yes

**GPU requirements**: Optional (GPU recommended for speed, CPU works)

**Model download size**: ~500MB-1GB (depending on vocoder)

**Expected inference speed**: Fast (seconds for short phrases on CPU, faster on GPU)

**Major limitations**:
- No pretrained Telugu model
- Requires custom phoneme dictionary for Telugu
- Diffusion sampling can be slower than other approaches

---

### 2. TCSinger

**Repository**: https://github.com/AaronZ345/TCSinger

**Last meaningful activity**: December 2024 (EMNLP 2024)

**License**: Not clearly specified (research code)

**Supported languages**: Chinese, English (pretrained only)

**Telugu support**: ❌ None
- Pretrained models only support Chinese and English
- Would require training on GTSinger dataset for multilingual

**Custom phoneme support**: Limited
- Uses phone_set.json for phonemes
- Would need to train custom model for Telugu

**Input format**:
- Phoneme sequence
- Target notes
- Target note durations
- Target note types (rest, lyric, slur)
- Prompt audio (required)

**Pitch supplied**: ✅ Yes (via target notes)

**Note duration supplied**: ✅ Yes

**Phoneme duration supplied**: ✅ Yes

**Output format**: WAV (48kHz)

**Python version**: Python 3.x

**macOS compatibility**: Likely (PyTorch)

**Apple Silicon compatibility**: Likely (PyTorch MPS)

**CPU support**: ✅ Yes

**GPU requirements**: Recommended

**Model download size**: Not specified (likely large)

**Expected inference speed**: Moderate

**Major limitations**:
- No Telugu support
- Requires training for multilingual
- Prompt audio required for every sample
- Research code, not production-ready

---

### 3. VocalRender

**Repository**: https://huggingface.co/pymaster/VocalRender

**Last meaningful activity**: 2024

**License**: Apache License 2.0

**Supported languages**: Mandarin Chinese (primary)

**Telugu support**: ❌ None
- Checkpoints primarily target Mandarin Chinese singing

**Custom phoneme support**: Limited
- Uses SVS tokenizer
- Would require training for Telugu

**Input format**:
- Lyrics
- MIDI pitches
- Symbolic note values
- Tempo
- Prompt audio (required)

**Pitch supplied**: ✅ Yes (via MIDI)

**Note duration supplied**: ✅ Yes (via symbolic note values)

**Phoneme duration supplied**: ❌ No (model predicts)

**Output format**: WAV (48kHz)

**Python version**: Python 3.x

**macOS compatibility**: ❌ No (requires CUDA)

**Apple Silicon compatibility**: ❌ No (requires CUDA)

**CPU support**: ❌ No (CUDA required)

**GPU requirements**: Required (CUDA-capable GPU)

**Model download size**: ~9.5GB

**Expected inference speed**: Slow (large model)

**Major limitations**:
- No Telugu support
- CUDA required (no Apple Silicon)
- Prompt audio required
- Very large model size
- No CPU support

---

### 4. VISinger 2

**Repository**: Paper-based, implementation varies

**Last meaningful activity**: 2023 (Interspeech 2023)

**License**: Varies by implementation

**Supported languages**: Mandarin Chinese (OpenCpop corpus)

**Telugu support**: ❌ None
- Trained on Mandarin Chinese only

**Custom phoneme support**: Limited
- Would require training for Telugu

**Input format**:
- Lyrics
- Musical score (note duration, note pitch)

**Pitch supplied**: ✅ Yes (via musical score)

**Note duration supplied**: ✅ Yes

**Phoneme duration supplied**: ⚠️ Partial (duration predictor)

**Output format**: WAV (44.1kHz)

**Python version**: Python 3.x

**macOS compatibility**: Likely (PyTorch)

**Apple Silicon compatibility**: Likely (PyTorch MPS)

**CPU support**: ✅ Yes

**GPU requirements**: Optional

**Model download size**: Moderate

**Expected inference speed**: Moderate

**Major limitations**:
- No Telugu support
- Would require training
- Implementation scattered across repos

---

### 5. NNSVS

**Repository**: https://github.com/nnsvs/nnsvs

**Last meaningful activity**: Active (documentation maintained)

**License**: MIT

**Supported languages**: 
- Japanese (primary)
- English (community support)
- **8+ languages via community voicebanks**

**Telugu support**: ⚠️ Possible via custom frontend
- Language-independent SVS design
- HTS-style full-context labels
- Custom frontend can be implemented
- Has been used for multiple languages by VocalSynth communities

**Custom phoneme support**: ✅ Excellent
- Language-independent design
- Custom frontend processing
- Can define any phoneme set

**Input format**:
- HTS-style full-context labels
- Phoneme sequence
- Pitch (F0)
- Timing

**Pitch supplied**: ✅ Yes

**Note duration supplied**: ✅ Yes

**Phoneme duration supplied**: ✅ Yes

**Output format**: WAV

**Python version**: Python 3.x

**macOS compatibility**: ✅ Yes

**Apple Silicon compatibility**: ✅ Yes (PyTorch MPS)

**CPU support**: ✅ Yes

**GPU requirements**: Optional

**Model download size**: Moderate (depends on voicebank)

**Expected inference speed**: Fast

**Major limitations**:
- No pretrained Telugu voicebank
- Requires custom frontend for Telugu
- Requires HTS-style labeling (complex)
- Steeper learning curve

---

## Telugu Phoneme Conversion Options

### 1. espeak-ng

**Repository**: https://github.com/espeak-ng/espeak-ng

**Telugu support**: ✅ Yes
- Language code: `te`
- Supports Telugu script (Unicode range 0xC00-0xC7F)
- Can generate IPA phonemes

**License**: GPL v3

**Input**: Telugu Unicode text

**Output**: IPA phonemes

**Availability**: ✅ Available now

**Pros**:
- Mature, widely used
- Telugu support built-in
- IPA output
- Can be called from Python via py-espeak-ng or subprocess

**Cons**:
- GPL license (viral)
- Pronunciation may not be optimal for singing
- Telugu-specific nuances may be imperfect

---

### 2. indic-g2p

**Repository**: https://github.com/Bindkushal/indic-g2p

**Telugu support**: ⏳ Planned
- Roadmap: v1.1 (Tamil + Telugu)
- Currently: Hindi (active), Punjabi, Bengali (beta)
- Not yet available for Telugu

**License**: Not specified (likely MIT/Apache)

**Input**: Indian language text

**Output**: IPA phonemes

**Availability**: ❌ Not yet for Telugu

**Pros**:
- Designed for neural TTS
- Native G2P for Indian languages
- Better linguistic handling than espeak

**Cons**:
- Telugu not yet implemented
- Would need to wait or contribute

---

### 3. MaryTTS TeluguLTS

**Repository**: https://marytts.github.io/

**Telugu support**: ✅ Yes
- TeluguLTS module
- Converts UTF8 graphemes to IT3 pronunciation

**License**: LGPL v3

**Input**: Telugu text

**Output**: IT3 phonemes

**Availability**: ✅ Available

**Pros**:
- Telugu-specific
- Linguistically accurate

**Cons**:
- Java-based (not Python-native)
- LGPL license
- IT3 format (not standard IPA)
- Integration complexity

---

### 4. Praxy (TTS reference only)

**Repository**: https://github.com/KarthikArigela/praxy

**Telugu support**: ✅ Yes (TTS)
- Telugu TTS with Chatterbox base + LoRA
- BUPS romanisation for Indic scripts

**License**: Not specified

**Input**: Telugu text

**Output**: Speech (not singing)

**Availability**: ✅ Available

**Pros**:
- Telugu support demonstrated
- Modern neural TTS

**Cons**:
- TTS, not singing synthesis
- Cannot follow melody/pitch
- Not suitable for our use case

---

## Recommended Approach

### Selected: DiffSinger + espeak-ng

**Rationale**:

1. **DiffSinger Advantages**:
   - Mature, actively maintained (OpenVPI)
   - Apache 2.0 license (permissive)
   - Custom phoneme dictionary support (can add Telugu)
   - Pitch control (F0 input)
   - Duration control (note and phoneme durations)
   - 44.1kHz output (high quality)
   - macOS and Apple Silicon compatible
   - CPU support available
   - Reasonable model size (~500MB-1GB)
   - Fast inference

2. **espeak-ng Advantages**:
   - Telugu support available now
   - IPA output (standard)
   - Can be called from Python
   - Mature, reliable

3. **Integration Path**:
   - Use espeak-ng to convert Telugu text → IPA phonemes
   - Map IPA phonemes to DiffSinger custom phoneme dictionary
   - Use our existing melody.json for pitch (F0)
   - Use our existing aligned_lyrics.json for timing/durations
   - Generate singing via DiffSinger

4. **No Training Required**:
   - Uses existing pretrained DiffSinger acoustic model
   - Only requires custom phoneme dictionary (no model training)
   - Leverages our existing pipeline

### Alternative: NNSVS + espeak-ng

**Rationale**:
- NNSVS is language-independent
- Custom frontend can be implemented
- HTS-style labels provide fine-grained control
- MIT license
- Good for research

**Drawbacks**:
- Steeper learning curve
- HTS labeling is complex
- Less mature tooling than DiffSinger
- Would require more development time

### Rejected Approaches

1. **TCSinger**: No Telugu support, requires training
2. **VocalRender**: No Telugu, CUDA required, too large
3. **VISinger 2**: No Telugu, requires training
4. **Praxy TTS**: TTS not singing, cannot follow melody
5. **Training custom Telugu model**: Requires significant data and compute

---

## Implementation Plan

### Phase 1: Telugu Phoneme Service
- Implement `TeluguPhonemeService` using espeak-ng
- Convert Telugu aksharas → IPA phonemes
- Test with sample Telugu text

### Phase 2: DiffSinger Integration
- Install DiffSinger dependencies
- Create custom Telugu phoneme dictionary
- Map IPA phonemes to DiffSinger format
- Implement `SingingSynthesisService` wrapper

### Phase 3: Proof of Concept
- Use short phrase: "నా చూపులే నీ ఊపిరై"
- Use existing melody.json for pitch
- Use existing aligned_lyrics.json for timing
- Generate 5-10 second test WAV
- Validate: Telugu intelligibility, melody following, timing

### Phase 4: Evaluation
- Manual listening test
- Assess Telugu pronunciation
- Assess melody following
- Assess timing accuracy
- Identify limitations

---

## Next Steps

1. Implement `TeluguPhonemeService` with espeak-ng
2. Create DiffSinger custom Telugu phoneme dictionary
3. Implement `SingingSynthesisService` with DiffSinger
4. Generate 5-10 second proof of concept
5. Manual validation before proceeding to full song

---

## Conclusion

**No pretrained Telugu singing model exists, but a viable path forward exists:**

**DiffSinger + espeak-ng** provides:
- ✅ Telugu phoneme conversion (via espeak-ng)
- ✅ Custom phoneme support (via DiffSinger)
- ✅ Pitch control (via melody.json)
- ✅ Duration control (via aligned_lyrics.json)
- ✅ No model training required
- ✅ Permissive license (Apache 2.0)
- ✅ macOS/Apple Silicon compatible
- ✅ CPU support available

This approach is technically realistic, requires no training, and leverages mature, open-source components.
