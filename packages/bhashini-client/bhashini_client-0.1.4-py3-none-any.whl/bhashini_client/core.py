from .utils.request_handler import RequestHandler
from .services.asr_service import ASRService
from .services.nmt_service import NMTService
from .services.tts_service import TTSService

class BhashiniClient:
    def __init__(self, api_key: str):
        self.handler = RequestHandler(api_key)
        self.asr_service = ASRService(self.handler)
        self.nmt_service = NMTService(self.handler)
        self.tts_service = TTSService(self.handler)

    def asr(
        self,
        audio_url: str,
        source_lang: str,
        serviceId=None,
        samplingRate=None,
        preProcessors=None,
        postProcessors=None,
    ):
        return self.asr_service.transcribe(
            audio_url,
            source_lang,
            serviceId,
            samplingRate,
            preProcessors,
            postProcessors,
        )

    def nmt(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        serviceId=None,
        numTranslation=None,
        preProcessors=None,
        postProcessors=None,
    ):
        return self.nmt_service.translate(
            text,
            source_lang,
            target_lang,
            serviceId,
            numTranslation,
            preProcessors,
            postProcessors,
        )

    # def tts(self, text: str, source_lang: str, gender="male", format_="wav"):
    #     return self.tts_service.synthesize(text, source_lang, gender, format_)

    def tts(self, text: str, source_lang: str, gender="male", format_="wav", save_to=None, serviceId=None, speed=None, samplingRate=None, preProcessors=None, postProcessors=None, return_base64=False):
        return self.tts_service.synthesize(text, source_lang, gender, format_, save_to, serviceId, speed, samplingRate, preProcessors, postProcessors, return_base64)