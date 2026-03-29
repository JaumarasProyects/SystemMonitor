"""
Text-to-Speech service using Edge TTS.
"""
import asyncio
import os
import re
import subprocess
from typing import Callable, Optional


class TTSService:
    """Text-to-Speech service using Microsoft Edge TTS."""
    
    EMOJI_REPLACEMENTS = {
        '👍': 'me gusta',
        '👎': 'no me gusta',
        '✅': 'hecho',
        '❌': 'error',
        '⚠️': 'atención',
        '🔊': '',
        '💻': '',
        '🧠': '',
        '⚡': '',
        '🌐': '',
        '📊': '',
        '📦': '',
        '🗑️': '',
        '🤖': '',
        '🔌': '',
        '👋': 'hola',
        '🎉': 'celebración',
        '🚀': 'lanzamiento',
        '💡': 'idea',
        '❤️': 'me gusta',
        '🔥': 'fuego',
        '⭐': 'estrella',
        '📝': 'nota',
        '💰': 'dinero',
        '🎯': 'objetivo',
        '🔒': 'seguro',
        '🔓': 'desbloqueado',
    }
    
    def __init__(self, voice: str = "es-ES-AlvaroNeural", rate: str = "+0%", volume: str = "+0%"):
        self.voice = voice
        self.rate = rate
        self.volume = volume
        self.enabled = False
        self._audio_playing = False
    
    def clean_text(self, text: str) -> str:
        """Clean text for TTS by removing special characters and emojis."""
        text = re.sub(r'[*#_~`>]+', ' ', text)
        text = re.sub(r'https?://\S+', '', text)
        
        for emoji, word in self.EMOJI_REPLACEMENTS.items():
            text = text.replace(emoji, word)
        
        text = re.sub(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]+', '', text)
        
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    async def _speak_async(self, text: str, audio_file: str):
        """Async method to generate and play audio."""
        import edge_tts
        
        communicate = edge_tts.Communicate(text, self.voice, 
                                           rate=self.rate, volume=self.volume)
        await communicate.save(audio_file)
        
        if os.path.exists(audio_file):
            import pygame
            pygame.mixer.init()
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play()
            self._audio_playing = True
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            pygame.mixer.quit()
            self._audio_playing = False
            try:
                os.remove(audio_file)
            except:
                pass
    
    def speak(self, text: str) -> bool:
        """Speak text using TTS. Returns True on success."""
        if not self.enabled:
            return False
        
        clean = self.clean_text(text)
        if not clean.strip():
            return False
        
        audio_file = os.path.join(os.path.dirname(__file__), "temp_tts.mp3")
        
        try:
            import edge_tts
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self._speak_async(clean, audio_file))
            loop.close()
            return True
        except Exception as e:
            print(f"TTS Error: {e}")
            return False
    
    def stop(self):
        """Stop currently playing audio."""
        try:
            import pygame
            if pygame.mixer.get_init():
                pygame.mixer.music.stop()
                pygame.mixer.quit()
            self._audio_playing = False
        except:
            pass
    
    @property
    def is_playing(self) -> bool:
        """Check if audio is currently playing."""
        return self._audio_playing
    
    def set_voice(self, voice: str):
        """Set the TTS voice."""
        self.voice = voice
    
    def set_rate(self, rate: str):
        """Set the TTS speaking rate."""
        self.rate = rate
    
    def set_volume(self, volume: str):
        """Set the TTS volume."""
        self.volume = volume
