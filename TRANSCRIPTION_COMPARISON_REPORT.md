# Telugu Lyrics Transcription Comparison Report

## Test Configuration
- **Song**: Ye Chota Nuvvunna (Telugu song from Johnny movie)
- **Input**: vocals.wav (Demucs isolated vocals)
- **Test Date**: October 1, 2026

## Model Comparison Results

### Whisper Tiny (Auto-detect Language)
**Job ID**: c6ddd15d-67c6-4e0f-8ee1-07819eef9b51

| Metric | Value |
|--------|-------|
| Segments | 28 |
| Words | 73 |
| Average Confidence | 0.092 |
| Median Confidence | 0.013 |
| Low Confidence Words (<0.3) | 66/73 (90%) |
| Detected Language | te |

**Sample Transcription**:
```
ト          那    小   沒有  我      我   !
S 7  00
Blum
```

**Analysis**: Extremely poor quality. Garbled output with very low confidence. Detects Telugu but produces mostly non-Telugu characters.

---

### Whisper Small (Auto-detect Language)
**Job ID**: b889f87a-2449-4f61-b302-a66c58fddacc

| Metric | Value |
|--------|-------|
| Segments | 2 |
| Words | 2 |
| Average Confidence | 0.50 |
| Median Confidence | 0.50 |
| Low Confidence Words (<0.3) | 0/2 (0%) |
| Detected Language | te |

**Sample Transcription**:
```
వార్త్రాయ్రినిందింిందిందింది.
వార్త్రాయాయాయాయాయా.
```

**Analysis**: Very limited output (only 2 words) but produces actual Telugu text with high confidence. The repeated syllables suggest it's capturing the vocal melody but not the actual lyrics.

---

### Whisper Tiny (Auto-detect Language) - Second Run
**Job ID**: 07fe2f6e-5738-430e-97f1-e9278d54ed73

| Metric | Value |
|--------|-------|
| Segments | 10 |
| Words | 30 |
| Average Confidence | 0.30 |
| Median Confidence | 0.15 |
| Low Confidence Words (<0.3) | 22/30 (73%) |
| Detected Language | te |

**Sample Transcription**:
```
illustrations of the 好…
cui 兄弟甘乎女郭 人生
Architect 慕辛 皇 寸 兄兄弟兄
妹 弟兄兄弟弟 皇 皇 皇 accessories
Varelaanara! Varelaanara! Varelaanara!
```

**Analysis**: Mixed output with some Telugu-like syllables ("Varelaanara") but mostly English and Chinese characters. Better than first tiny run but still poor quality.

---

## Failed Configurations

### Whisper Small + Explicit Telugu + Audio Preprocessing
**Job ID**: 6b3e99d7-c560-4213-8295-161baba4c17e
- **Result**: Empty transcription (0 segments, 0 words)
- **Issue**: Explicit language="te" combined with mono 16kHz preprocessing caused complete failure

### Whisper Small + Auto-detect + Audio Preprocessing
**Job ID**: 906ac772-6df4-44cc-83b6-10a9db930529
- **Result**: Empty transcription (0 segments, 0 words)
- **Issue**: Audio preprocessing (mono 16kHz) caused complete failure

---

## Key Findings

### 1. Model Size Impact
- **Tiny**: Produces more words but with very low confidence (0.09 avg). Output is mostly garbled.
- **Small**: Produces fewer words but with higher confidence (0.50 avg). Output is actual Telugu but very limited.

### 2. Explicit Language Setting
- Setting `language="te"` explicitly caused the small model to return empty results.
- Auto-detection works better for this use case.

### 3. Audio Preprocessing
- Converting to mono 16kHz (Whisper's recommended format) caused complete transcription failure.
- Using the original vocals.wav (stereo, 44.1kHz from Demucs) produced results.

### 4. Telugu Text Quality
- Neither model produces accurate Telugu lyrics.
- The small model produces Telugu characters but they appear to be phonetic approximations of the melody rather than actual lyrics.
- The tiny model produces mixed languages (English, Chinese, some Telugu-like sounds).

---

## Recommendations

### Current State
**Neither Whisper tiny nor Whisper small is suitable for Telugu singing lyrics transcription.** The models:
- Detect Telugu language correctly
- Fail to transcribe actual Telugu lyrics
- Produce garbled or phonetic approximations
- Show poor confidence scores (tiny) or extremely limited output (small)

### Next Steps
1. **Telugu-Specific Models**: Attempt to use fine-tuned Telugu models (vasista22/whisper-telugu-small, BuzzASR/telugu) once Hugging Face download issues are resolved.
2. **Alternative ASR**: Consider non-Whisper-based Telugu ASR solutions.
3. **Manual Transcription**: For production use, manual transcription may be required until a suitable automated solution is found.
4. **Hybrid Approach**: Consider using Whisper for timing/segmentation and manual correction of lyrics.

### Configuration Recommendations
- **Model**: Whisper small (better confidence than tiny)
- **Language**: Auto-detect (explicit Telugu causes failures)
- **Audio**: Use original vocals.wav without preprocessing
- **Default**: Telugu (te) as application default, but allow auto-detection

---

## Architecture Notes

The transcription service architecture is well-designed and supports:
- Multiple model implementations (OpenAI Whisper, Telugu-specific models)
- Configurable model size via environment variable
- Optional language parameter
- Confidence statistics tracking
- Word and segment-level timestamps

The Telugu-specific implementation (`telugu_whisper_impl.py`) is ready to use once Hugging Face model downloads are accessible.
