---
license: cc-by-4.0
base_model: ResembleAI/chatterbox
base_model_relation: finetune
language:
- te
library_name: chatterbox
pipeline_tag: text-to-speech
tags:
- text-to-speech
- tts
- chatterbox
- telugu
- indian-languages
- code-switching
- voice-cloning
---

# Chatterbox-Multilingual — Telugu (te) fine-tune

A **Telugu** fine-tune of Resemble AI's
[`ResembleAI/chatterbox`](https://huggingface.co/ResembleAI/chatterbox) (Chatterbox-Multilingual,
checkpoint `t3_mtl23ls_v2.safetensors`). It adds Telugu — including **code-switched** (Telugu+English,
e.g. "Tenglish") speech — while keeping the base model's English and 23-language ability and
its zero-shot voice cloning. This is a *derivative* of Chatterbox; see the model tree above.

## Key details

- **Backbone:** Chatterbox **T3** (~0.5B Llama) text→speech-token model, warm-started from the
  released 23-language checkpoint (English/cross-lingual ability preserved).
- **Adaptation:** LoRA (rank 16, merged into the weights) + retrained text embedding/head.
- **Tokenizer:** the multilingual grapheme tokenizer **extended with the Telugu script** and a
  `[te]` language tag (vocab 2521).
- **Training:** 10,000 steps on ~34.5k Telugu clips (see *Training data*).
- **Voice cloning:** zero-shot from a 6–15s reference clip, same as base.
- **Watermark:** every output carries Resemble AI's **PerTh** neural watermark.

## What was kept vs. changed

Only the **text side** is Telugu-specific; the language-agnostic **acoustic stack is reused
unchanged** from the base model.

| Component | Role | In this fine-tune |
|---|---|---|
| **T3** (Llama ~0.5B) | text tokens → speech tokens | **Trained** (LoRA + text emb/head), merged into `t3_mtl_te.safetensors` |
| **Grapheme tokenizer** | text → token ids | **Extended** (+Telugu script, `[te]` tag) |
| **S3Gen + HiFi-GAN** | speech tokens → waveform | **Kept unchanged** (`s3gen.pt`) |
| **VoiceEncoder** | speaker embedding | **Kept unchanged** (`ve.pt`) |
| **S3Tokenizer** | wav → speech tokens | **Kept unchanged** (from base) |
| **Conditioning / misc** | default conds, ZH tokenizer | **Kept unchanged** (`conds.pt`, `Cangjie5_TC.json`) |

The bundled `s3gen.pt`, `ve.pt`, `conds.pt`, and `Cangjie5_TC.json` are **Resemble AI's original
files, redistributed unchanged** under their MIT license (see *License & attribution*).

## Training data

Trained only on **CC-BY-4.0** Telugu speech (attribution below). Only model **weights** are
published here — **no raw dataset audio** is redistributed.

| Dataset | Content | License |
|---|---|---|
| [`google/fleurs`](https://huggingface.co/datasets/google/fleurs) (`te_in`) | ~5 h read speech, 16 kHz | CC-BY-4.0 |
| [`ai4bharat/indicvoices_r`](https://huggingface.co/datasets/ai4bharat/indicvoices_r) (Telugu) | multi-speaker, 48 kHz | CC-BY-4.0 |

> OpenSLR **SLR66** (CC-BY-**SA**-4.0) was **deliberately excluded** so the training mix stays
> CC-BY-4.0 and this model can be released under a plain CC-BY-4.0 license (no ShareAlike).

## Usage

```python
import torchaudio as ta
from huggingface_hub import snapshot_download
from chatterbox.mtl_tts import ChatterboxMultilingualTTS

ckpt = snapshot_download("shankarpandala/chatterbox-telugu")
model = ChatterboxMultilingualTTS.from_local(ckpt, device="mps", t3_model="t3_mtl_te.safetensors")

# Pure Telugu
wav = model.generate(
    "నమస్కారం, ఈ రోజు ఎలా ఉన్నారు?",
    language_id="te",
    audio_prompt_path="your_reference.wav",   # 6-15s clip of the target voice
)
ta.save("out.wav", wav, model.sr)

# Code-switched (Telugu + English)
wav = model.generate("నేను office కి వెళ్తున్నాను, evening meeting ఉంది.", language_id="te", audio_prompt_path="your_reference.wav")
ta.save("out_codeswitch.wav", wav, model.sr)
```

`device="cuda"` on a GPU, `"mps"` on Apple Silicon, `"cpu"` otherwise.

## Watermarking

Like the base model, **every audio file generated carries Resemble AI's PerTh neural
watermark** — imperceptible marks that survive MP3 compression and common edits — for
responsible-AI provenance.

## Acknowledgements

- **Resemble AI** for [Chatterbox](https://huggingface.co/ResembleAI/chatterbox) (which itself builds on
  CosyVoice, HiFT-GAN, and Llama 3).
- **AI4Bharat** for IndicVoices-R and the **Google** FLEURS team for the Telugu data.

## License & attribution

- **This model:** released under **CC-BY-4.0** (attribution required; commercial use and
  derivatives permitted). This carries forward the CC-BY-4.0 attribution required by the
  training data.
- **Base model:** [`ResembleAI/chatterbox`](https://huggingface.co/ResembleAI/chatterbox) — **MIT © Resemble AI**.
  The redistributed acoustic files (`s3gen.pt`, `ve.pt`, `conds.pt`, `Cangjie5_TC.json`) remain
  under that MIT license:

  > Permission is hereby granted, free of charge, to any person obtaining a copy of this software
  > and associated documentation files... The above copyright notice and this permission notice
  > shall be included in all copies. (MIT, © 2025 Resemble AI — full text:
  > https://github.com/resemble-ai/chatterbox/blob/master/LICENSE)

- **Training data:** FLEURS and IndicVoices-R, both **CC-BY-4.0** (cited below). CC-BY-SA SLR66
  was excluded to keep this release CC-BY-4.0.

## Citations

```bibtex
@misc{chatterboxtts2025,
  author       = {{Resemble AI}},
  title        = {{Chatterbox-TTS}},
  year         = {2025},
  howpublished = {\url{https://github.com/resemble-ai/chatterbox}},
  note         = {GitHub repository},
}

@inproceedings{conneau2023fleurs,
  title     = {{FLEURS}: Few-Shot Learning Evaluation of Universal Representations of Speech},
  author    = {Conneau, Alexis and Ma, Min and Khanuja, Simran and Zhang, Yu and
               Axelrod, Vera and Dalmia, Siddharth and Riesa, Jason and Rivera, Clara and
               Bapna, Ankur},
  booktitle = {2022 IEEE Spoken Language Technology Workshop (SLT)},
  pages     = {798--805},
  year      = {2023},
  doi       = {10.1109/SLT54892.2023.10023141},
  note      = {arXiv:2205.12446},
}

@inproceedings{sankar2024indicvoicesr,
  title     = {{IndicVoices-R}: Unlocking a Massive Multilingual Multi-speaker Speech
               Corpus for Scaling Indian {TTS}},
  author    = {Sankar, Ashwin and Anand, Srija and Varadhan, Praveen Srinivasa and
               Thomas, Sherry and Singal, Mehak and Kumar, Shridhar and Mehendale, Deovrat and
               Krishana, Aditi and Raju, Giri and Khapra, Mitesh M.},
  booktitle = {Advances in Neural Information Processing Systems 38 (NeurIPS 2024)},
  year      = {2024},
  url       = {http://papers.nips.cc/paper_files/paper/2024/hash/7dfcaf4512bbf2a807a783b90afb6c09-Abstract-Datasets_and_Benchmarks_Track.html},
}
```

## Disclaimer & limitations

Focused on Telugu and Telugu+English code-switching; it does **not** match Chatterbox's
English SOTA quality. Use responsibly — do not use it to impersonate real people without consent or
to produce misleading content. All outputs are PerTh-watermarked.
