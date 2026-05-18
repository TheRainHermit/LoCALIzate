# backend/app/services/audio_service.py

from google.cloud import texttospeech
from app.ml.ux_writing import generate_caleño_narrative
import aiofiles
import os

class AudioService:
    def __init__(self):
        self.tts_client = texttospeech.TextToSpeechClient()
    
    async def generate_narration(self, lugar_id: int, user_profile: dict) -> str:
        """
        Crea audio-guía personalizado:
        
        1. Obtener información del lugar
        2. Generar narrativa con UX Writing caleño
        3. Sintetizar con Google Cloud TTS
        4. Guardar en Supabase Storage
        5. Retornar URL
        """
        
        from app.services.lugar_service import LugarService
        lugar_service = LugarService()
        lugar = await lugar_service.get_by_id(lugar_id)
        
        # 1. Generar narrativa (caleño tone)
        narrative = generate_caleño_narrative(
            lugar=lugar,
            user_style=user_profile.get('estilo_viaje', 'cultural'),
            tone='enthusiastic'  # Ej. si es salsa, tono vibrante
        )
        
        # 2. Sintetizar con TTS
        synthesis_input = texttospeech.SynthesisInput(text=narrative)
        
        voice = texttospeech.VoiceSelectionParams(
            language_code="es-CO",  # Español Colombia
            name="es-CO-Neural2-C",  # Voz neural Colombiana
        )
        
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=0.9,  # Hablar un poco más lento
        )
        
        response = self.tts_client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config,
        )
        
        # 3. Guardar en Supabase Storage
        audio_filename = f"audios/{lugar_id}_{user_profile['estilo_viaje']}.mp3"
        
        supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        supabase.storage.from_('audios').upload(
            audio_filename,
            response.audio_content
        )
        
        # 4. Obtener URL pública
        audio_url = supabase.storage.from_('audios').get_public_url(audio_filename)
        
        # 5. Guardar en DB
        await self.save_audio_record(
            lugar_id=lugar_id,
            audio_url=audio_url,
            transcripcion=narrative,
            duracion_segundos=len(response.audio_content) // 2000  # Aprox
        )
        
        return audio_url
    
    async def save_audio_record(self, lugar_id, audio_url, transcripcion, duracion_segundos):
        """Guarda referencia del audio en audios_guia"""
        from supabase import create_client
        
        supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        
        supabase.table('audios_guia').insert({
            'lugar_id': lugar_id,
            'audio_url': audio_url,
            'transcripcion': transcripcion,
            'duracion_segundos': duracion_segundos,
            'tipo_voz': 'caleña',
            'idioma': 'es'
        }).execute()