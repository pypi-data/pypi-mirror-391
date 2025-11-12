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

# ASR basics
print(client.asr("https://example.com/audio.wav", "te"))

# ASR with explicit configuration
print(
    client.asr(
        "https://example.com/audio.wav",
        "te",
        serviceId="bhashini/ai4bharat/conformer-multilingual-asr",
        samplingRate=44100,
    )
)

# NMT with optional processors
print(
    client.nmt(
        "What are you doing?",
        "en",
        "hi",
        numTranslation="False",
        preProcessors=["glossary"],
        postProcessors=["glossary"],
    )
)

# TTS with preprocessing and file output
print(
    client.tts(
        "मेरा नाम विहिर है",
        "en",
        save_to="output_audio.wav",
        gender="female",
        preProcessors=["text-normalization"],
        postProcessors=["high-compression"],
    )
)
```
