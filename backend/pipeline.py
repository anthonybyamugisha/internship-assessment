"""
Pipeline orchestration: Audio → STT → Summarize → Translate → TTS
"""

import os
import tempfile
from pathlib import Path
from typing import Optional, Tuple
from .sunbird_client import SunbirdClient
from mutagen import File as MutagenFile


class Pipeline:
    """Orchestrates the full GenAI pipeline."""
    
    MAX_AUDIO_DURATION_MINUTES = 5
    
    def __init__(self, client: SunbirdClient):
        """Initialize with Sunbird API client."""
        self.client = client
    
    def _get_audio_duration(self, audio_path: str) -> float:
        """
        Get audio duration in minutes using mutagen.
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Duration in minutes
            
        Raises:
            ValueError: If audio format unsupported or unreadable
        """
        try:
            audio = MutagenFile(audio_path)
            if audio is None or not hasattr(audio, 'info') or audio.info is None:
                raise ValueError("Unsupported or corrupted audio format")
            return audio.info.length / 60.0
        except Exception as e:
            raise ValueError(f"Could not determine audio duration: {e}")
    
    def process_audio_input(self, audio_path: str, target_language: str) -> dict:
        """
        Full pipeline: audio → transcript → summary → translation → speech.
        
        Args:
            audio_path: Path to input audio file
            target_language: Language code (lug, ach, teo, lgg, nyn)
            
        Returns:
            Dictionary with all intermediate and final results
            
        Raises:
            ValueError: If audio exceeds duration limit
            Exception: On any processing failure
        """
        # Check audio duration (5 min max per requirement)
        duration_min = self._get_audio_duration(audio_path)
        if duration_min > self.MAX_AUDIO_DURATION_MINUTES:
            raise ValueError(
                f"Audio file is too long ({duration_min:.1f} min). "
                f"Maximum allowed is {self.MAX_AUDIO_DURATION_MINUTES} minutes."
            )
        
        # Step 1: Transcribe audio
        transcript = self.client.transcribe_audio(audio_path)
        
        # Step 2: Summarize transcript
        summary = self.client.summarize_text(transcript)
        
        # Step 3: Translate summary
        translated = self.client.translate_text(summary, target_language)
        
        # Step 4: Synthesize speech from translation
        audio_url = self.client.synthesize_speech(translated, target_language)
        
        return {
            "original_audio_path": audio_path,
            "transcript": transcript,
            "summary": summary,
            "translated_summary": translated,
            "translated_audio_url": audio_url,
            "target_language": target_language,
            "audio_duration_min": duration_min,
        }
    
    def process_text_input(self, text: str, target_language: str) -> dict:
        """
        Pipeline for direct text input: text → summarize → translate → speech.
        
        Args:
            text: Input text
            target_language: Target language code
            
        Returns:
            Dictionary with all intermediate and final results
        """
        # Step 1: Summarize text
        summary = self.client.summarize_text(text)
        
        # Step 2: Translate summary
        translated = self.client.translate_text(summary, target_language)
        
        # Step 3: Synthesize speech
        audio_url = self.client.synthesize_speech(translated, target_language)
        
        return {
            "original_text": text,
            "summary": summary,
            "translated_summary": translated,
            "translated_audio_url": audio_url,
            "target_language": target_language
        }
