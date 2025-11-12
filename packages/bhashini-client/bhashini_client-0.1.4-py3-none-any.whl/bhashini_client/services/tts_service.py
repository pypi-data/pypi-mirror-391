import base64
from pathlib import Path
from typing import List, Optional


class TTSService:
    """Service for Text-to-Speech (TTS) synthesis operations."""
    
    def __init__(self, handler):
        """Initialize TTS service with a request handler.
        
        Args:
            handler: Request handler instance for making API calls.
        """
        self.handler = handler

    def synthesize(self, 
    text: str, 
    source_lang: str, 
    gender: Optional[str] = None, 
    format_: str = "wav", 
    save_to: Optional[str] = None,
    serviceId: Optional[str] = None,
    speed: Optional[float] = None,
    samplingRate: Optional[int] = None,
    preProcessors: Optional[List[str]] = None,
    postProcessors: Optional[List[str]] = None,
    return_base64: bool = False
    ):
        """Synthesize speech from text using TTS.
        
        Converts text to speech audio using the Bhashini Text-to-Speech service.
        The generated audio can be returned as a URI or saved to a local file.
        
        Args:
            text (str): Text to be converted to speech.
            source_lang (str): Source language code (e.g., "hi", "en", "te", "gu").
                Supported language codes can be found in the Bhashini documentation.
            gender (Optional[str]): Voice gender. Accepts "male" or "female".
                If not provided, defaults to "female".
            format_ (str): Audio format. Defaults to "wav". Other formats may be
                supported depending on the service configuration.
            save_to (Optional[str]): File path to save the audio file. If provided,
                the audio will be saved to this location. If not provided and audio
                content is returned, defaults to "tts_output.wav" in the current
                directory. If None and audio URI is returned, returns the URI string.
            serviceId (Optional[str]): Custom service ID for TTS. If not provided,
                defaults to "ai4bharat/indic-tts-coqui-indo_aryan-gpu--t4".
            speed (Optional[float]): Speech speed/rate. Valid range: 0.1 to 1.99.
                If not provided, defaults to 1.0 (normal speed).
            samplingRate (Optional[int]): Audio sampling rate in Hz. If not provided,
                defaults to 48000. Common values: 16000, 24000, 44100, 48000.
            preProcessors (Optional[List[str]]): Optional list of preprocessors applied before synthesis
                (e.g., ["text-normalization"]). Omitted from payload if not provided.
            postProcessors (Optional[List[str]]): Optional list of postprocessors applied after synthesis
                (e.g., ["high-compression"] or ["low-compression"]). Omitted from payload if not provided.
            return_base64 (bool): If True, return raw base64 audio content when available.
                Otherwise, return URI or save to file (default behavior).
        
        Returns:
            str: Path to the saved audio file if `save_to` is provided or audio content
                is returned, or the audio URI string if available. Returns empty string
                if synthesis fails or no audio content/URI is received.
        
        Example:
            >>> service = TTSService(handler)
            >>> # Basic usage
            >>> audio_path = service.synthesize(
            ...     "Hello, how are you?",
            ...     "en",
            ...     save_to="output.wav"
            ... )
            >>> # With custom parameters
            >>> audio_path = service.synthesize(
            ...     "Hello, how are you?",
            ...     "en",
            ...     gender="male",
            ...     save_to="output.wav",
            ...     serviceId="custom-service-id",
            ...     speed=1.5,
            ...     samplingRate=44100,
            ...     preProcessors=["text-normalization"],
            ...     postProcessors=["high-compression"]
            ... )
            >>> # Return base64 content instead of saving/URI
            >>> audio_b64 = service.synthesize(
            ...     "Hello",
            ...     "en",
            ...     return_base64=True
            ... )
        """
        gender = gender or "female"
        serviceId = serviceId or "ai4bharat/indic-tts-coqui-indo_aryan-gpu--t4"
        speed = speed or 1.0
        samplingRate = samplingRate or 48000
        
        config = {
            "language": {"sourceLanguage": source_lang},
            "serviceId": serviceId,
            "gender": gender,
            "audioFormat": format_,
            "speed": speed,
            "samplingRate": samplingRate
        }

        if preProcessors:
            config["preProcessors"] = preProcessors
        if postProcessors:
            config["postProcessors"] = postProcessors

        payload = {
            "pipelineTasks": [
                {
                    "taskType": "tts",
                    "config": config
                }
            ],
            "inputData": {"input": [{"source": text}]}
        }
        result = self.handler.post(payload)
        audio = result.get("pipelineResponse", [{}])[0].get("audio", [{}])[0]
        uri = audio.get("audioUri")
        content = audio.get("audioContent")

        if return_base64:
            if content:
                return content
            if uri:
                return uri
            return ""

        if uri:
            return uri
        if not content:
            return ""

        target = Path(save_to or "tts_output.wav")
        if not target.suffix:
            target = target.with_suffix(".wav")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(base64.b64decode(content))
        return str(target.resolve())


#service id, gender, samplerate, speed, langugae - serviceID, text normaliztion, high|low compression, 