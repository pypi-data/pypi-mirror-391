# bhashini-client

A simple Python client library for interacting with [Bhashini](https://bhashini.gov.in/) inference APIs.  
Currently supports:
- **ASR** (Automatic Speech Recognition)
- **NMT** (Machine Translation)
- **TTS** (Text-to-Speech)


## Installation

```bash
pip install bhashini-client
```


## Example Usage
```python
from bhashini_client import BhashiniClient

client = BhashiniClient(api_key="api-key")

# --- ASR (Speech -> Text) ---
# Basic ASR (default settings)
asr_text = client.asr("https://example.com/audio.wav", "te")
print("ASR Basic:", asr_text)

# ASR with explicit configuration
asr_custom = client.asr(
    "https://example.com/audio.wav",
    "te",
    serviceId="bhashini/ai4bharat/conformer-multilingual-asr",
    samplingRate=44100,
)
print("ASR Custom:", asr_custom)


# --- NMT (Translate) ---
# Basic NMT: English -> Hindi
nmt_text = client.nmt("What are you doing?", "en", "hi")
print("NMT Basic:", nmt_text)

# NMT with processors (example: glossary)
nmt_proc = client.nmt(
    "What are you doing?",
    "en",
    "hi",
    numTranslation="False",
    preProcessors=["glossary"],
    postProcessors=["glossary"],
)
print("NMT With Processors:", nmt_proc)


# --- TTS (Text -> Speech) ---
# 1) Basic TTS: Hindi text with correct language code; saves to file
tts_basic_path = client.tts(
    "मेरा नाम विहिर है",
    "hi",
    save_to="tts_basic.wav",
)
print("TTS Basic (file):", tts_basic_path)

# 2) TTS with explicit gender and custom speed/sampling
tts_tuned_path = client.tts(
    "मेरा नाम विहिर है",
    "hi",
    gender="female",
    speed=0.9,              # 0.1 to 1.99
    samplingRate=24000,     # e.g., 16000/24000/44100/48000
    save_to="tts_tuned.wav",
)
print("TTS Tuned (file):", tts_tuned_path)

# 3) TTS with processors
#    Pre:  text-normalization
#    Post: high-compression (smaller file ~64kbps) or low-compression (~128kbps)
tts_proc_path = client.tts(
    "मेरा नाम विहिर है",
    "hi",
    save_to="tts_processed.wav",
    gender="female",
    preProcessors=["text-normalization"],
    postProcessors=["high-compression"],
)
print("TTS With Processors (file):", tts_proc_path)

# 4) TTS returning base64 audio instead of saving
tts_b64 = client.tts(
    "मेरा नाम विहिर है",
    "hi",
    return_base64=True,
    preProcessors=["text-normalization"],
    postProcessors=["low-compression"],
)
print("TTS Base64 (first 60 chars):", tts_b64[:60] if isinstance(tts_b64, str) else tts_b64)

# 5) English TTS with a custom service (when using English text)
tts_en_path = client.tts(
    "My name is Vihir",
    "en",
    save_to="tts_en.wav",
    gender="female",
    serviceId="ai4bharat/indic-tts-coqui-misc-gpu--t4",
)
print("TTS English (file):", tts_en_path)

# Notes:
# - If the server returns an audio URI instead of content, the client returns that URI string.
# - Use the correct source language for your text, e.g., "hi" for Hindi, "en" for English.
# - preProcessors and postProcessors are optional. See README for supported values.
```
