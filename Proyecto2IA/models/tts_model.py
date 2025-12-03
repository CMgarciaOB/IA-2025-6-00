import os
import asyncio
import edge_tts

BASE_AUDIO_DIR = "audio"
os.makedirs(BASE_AUDIO_DIR, exist_ok=True)


VALID_VOICES = {
    "es-ES-AlvaroNeural",
    "es-ES-ElviraNeural",
    "es-MX-DaliaNeural",
    "es-MX-JorgeNeural",
}

class TTSPipeline:
    def __init__(self):
        pass

    def synthesize(
        self,
        text: str,
        audio_path: str,
        voice: str = "es-ES-JorgeNeural"
    ) -> str:
        if not text or not text.strip():
            raise ValueError("[TTS] Texto vacío, no se puede sintetizar.")

        if voice not in VALID_VOICES:
            voice = "es-ES-DaliaNeural"

        os.makedirs(os.path.dirname(audio_path) if os.path.dirname(audio_path) else '.', exist_ok=True)

        # damos la extension .mp3
        root, _ext = os.path.splitext(audio_path)
        full_path = root + ".mp3"

        # Ejecutar edge-tts de forma síncrona
        asyncio.run(self._async_synthesize(text, full_path, voice))
        
        return full_path

    async def _async_synthesize(self, text: str, output_path: str, voice: str):
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_path)

# se usara el pipline desde el main mediante este valor
tts_pipeline = TTSPipeline()