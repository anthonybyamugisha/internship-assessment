"""
Sunbird AI API Client - optimized wrapper around Sunbird endpoints
"""

import os
import requests
from typing import Optional, Dict, Any, Callable
from pathlib import Path
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class SunbirdClient:
    """Optimized client for interacting with Sunbird AI API."""
    
    BASE_URL = "https://api.sunbird.ai"
    
    # TTS speaker IDs for Ugandan languages
    SPEAKER_IDS = {
        "ach": 241,  # Acholi (Female)
        "teo": 242,  # Ateso (Female)
        "nyn": 243,  # Runyankole (Female)
        "lgg": 245,  # Lugbara (Female)
        "lug": 248,  # Luganda (Female)
    }
    
    def __init__(self, api_token: str):
        """Initialize with API token."""
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        })
        
        # Configure connection pooling and retries for better performance
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST"]
        )
        adapter = HTTPAdapter(
            pool_connections=10,
            pool_maxsize=10,
            max_retries=retry_strategy,
            pool_block=False
        )
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
    
    def transcribe_audio(self, audio_path: str, language: Optional[str] = None) -> str:
        """
        Transcribe audio to text using STT API.
        
        Args:
            audio_path: Path to audio file
            language: Optional language code (e.g., 'eng', 'lug', 'ach')
            
        Returns:
            Transcribed text
            
        Raises:
            requests.RequestException: On API failure
        """
        url = f"{self.BASE_URL}/tasks/modal/stt"
        
        with open(audio_path, 'rb') as f:
            files = {'audio': f}
            data = {}
            if language:
                data['language'] = language
            
            response = self.session.post(url, files=files, data=data)
            response.raise_for_status()
            
        result = response.json()
        return result.get('audio_transcription', '')
    
    def summarize_text(self, text: str) -> str:
        """
        Summarize text using Sunflower LLM.
        
        Args:
            text: Input text to summarize
            
        Returns:
            Summary text
        """
        prompt = f"Please summarize the following text concisely:\n\n{text}"
        return self._simple_inference(prompt)
    
    def translate_text(self, text: str, target_language: str) -> str:
        """
        Translate text to target Ugandan language using Sunflower LLM.
        
        Args:
            text: Text to translate
            target_language: Language code ('lug', 'ach', 'teo', 'lgg', 'nyn')
            
        Returns:
            Translated text
        """
        language_names = {
            "lug": "Luganda",
            "ach": "Acholi",
            "teo": "Ateso",
            "lgg": "Lugbara",
            "nyn": "Runyankole"
        }
        
        lang_name = language_names.get(target_language, target_language)
        prompt = f"Translate the following text to {lang_name}. Return only the translation, no explanations:\n\n{text}"
        return self._simple_inference(prompt)
    
    def synthesize_speech(self, text: str, language: str = "lug") -> str:
        """
        Convert text to speech using TTS API.
        
        Args:
            text: Text to convert to speech
            language: Language code for speaker selection (default: Luganda)
            
        Returns:
            URL to the generated audio file (temporary signed URL)
            
        Raises:
            requests.RequestException: On API failure
        """
        url = f"{self.BASE_URL}/tasks/modal/tts"
        
        speaker_id = self.SPEAKER_IDS.get(language, 248)  # Default to Luganda
        
        payload = {
            "text": text,
            "speaker_id": speaker_id
        }
        
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        
        result = response.json()
        return result.get('output', {}).get('audio_url', '')
    
    def _simple_inference(self, instruction: str, temperature: float = 0.3) -> str:
        """
        Call Sunflower inference endpoint (chat format).
        
        Args:
            instruction: User instruction/prompt
            temperature: Sampling temperature (0.0 - 2.0)
            
        Returns:
            Model response content
        """
        url = f"{self.BASE_URL}/tasks/sunflower_inference"
        
        payload = {
            "messages": [
                {"role": "user", "content": instruction}
            ],
            "temperature": temperature
        }
        
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        
        result = response.json()
        # Response format: {"content": "...", "model_type": "...", ...}
        return result.get('content', '')
