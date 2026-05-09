"""
Sunbird AI Voice Translator - Streamlit Application
"""

import os
from typing import Optional
from dotenv import load_dotenv
import streamlit as st
from pathlib import Path
from backend.sunbird_client import SunbirdClient
from backend.pipeline import Pipeline
import tempfile
import requests
import librosa

# Load .env file automatically from project root
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# Page configuration
st.set_page_config(
    page_title="Sunbird AI Voice Translator",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.1rem;
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .result-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .error-box {
        background-color: #f8d7da;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Load API token from environment
API_TOKEN = os.getenv("SUNBIRD_API_TOKEN")
if not API_TOKEN:
    st.error("""
    ### ❌ Missing API Token
    
    The `SUNBIRD_API_TOKEN` environment variable is not set.
    
    **To fix this:**
    1. Create a `.env` file in the project directory
    2. Add: `SUNBIRD_API_TOKEN=your_token_here`
    3. Or set it as a secret in Hugging Face Spaces
    
    Get your token from: https://api.sunbird.ai/
    """)
    st.stop()

# Initialize client and pipeline
@st.cache_resource
def initialize_pipeline():
    """Initialize the Sunbird client and pipeline (cached)."""
    client = SunbirdClient(API_TOKEN)
    pipeline = Pipeline(client)
    return pipeline

pipeline = initialize_pipeline()

# Language configuration
LANGUAGES = {
    "Luganda": "lug",
    "Runyankole": "nyn",
    "Acholi": "ach",
    "Ateso": "teo",
    "Lugbara": "lgg"
}

# Constants
MAX_AUDIO_MINUTES = 5


def validate_audio_duration(audio_path: str) -> tuple[bool, float]:
    """
    Check if audio file is within duration limit.
    Returns (is_valid, duration_in_minutes).
    """
    try:
        duration = librosa.get_duration(filename=audio_path)
        return duration <= (MAX_AUDIO_MINUTES * 60), duration / 60
    except Exception:
        # If we can't determine, assume valid but warn
        return True, 0.0


def download_audio(audio_url: str) -> Optional[bytes]:
    """Download audio from URL and return as bytes."""
    try:
        response = requests.get(audio_url, stream=True)
        response.raise_for_status()
        return response.content
    except Exception as e:
        st.error(f"Failed to download audio: {e}")
        return None


def get_audio_mime_type(url: str) -> str:
    """Determine MIME type from URL or default to mp3."""
    if '.wav' in url.lower():
        return 'audio/wav'
    elif '.ogg' in url.lower():
        return 'audio/ogg'
    elif '.m4a' in url.lower():
        return 'audio/m4a'
    return 'audio/mp3'


# ============ MAIN UI ============
st.markdown('<h1 class="main-header">🌍 Sunbird AI Voice Translator</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Transform your voice or text into summaries, then translate and speak them in Ugandan languages.</p>', unsafe_allow_html=True)

# Sidebar with information
with st.sidebar:
    st.header("ℹ️ About")
    st.markdown("""
    This app uses **Sunbird AI** to:
    1. **Transcribe** audio to text
    2. **Summarize** the content
    3. **Translate** to Ugandan languages
    4. **Generate speech** of the translation
    
    **Supported Languages:**
    - Luganda
    - Runyankole
    - Acholi
    - Ateso
    - Lugbara
    """)
    
    st.info("📝 **Note:** Audio files must be under 5 minutes.")
    
    st.markdown("---")
    st.markdown("**Powered by [Sunbird AI](https://sunbird.ai)**")

# Main content area with tabs
tab1, tab2 = st.tabs(["✍️ Text Input", "🎙️ Audio Upload"])

# ============ TEXT INPUT TAB ============
with tab1:
    st.header("Enter Your Text")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        text_input = st.text_area(
            "Your Text",
            placeholder="Type or paste your text here...",
            height=200
        )
        
        target_language = st.selectbox(
            "Translate to",
            options=list(LANGUAGES.keys()),
            index=0
        )
        
        process_text_btn = st.button("🔄 Process Text", type="primary", use_container_width=True)
    
    with col2:
        if process_text_btn:
            if not text_input or not text_input.strip():
                st.warning("Please enter some text.")
            else:
                with st.spinner("Processing your text..."):
                    try:
                        target_lang = LANGUAGES[target_language]
                        result = pipeline.process_text_input(text_input.strip(), target_lang)
                        
                        # Display results
                        st.success("✅ Processing complete!")
                        
                        st.markdown("### 📝 Summary")
                        st.write(result["summary"])
                        
                        st.markdown("### 🌐 Translated Summary")
                        st.write(result["translated_summary"])
                        
                        # Download and display audio
                        if result.get("translated_audio_url"):
                            st.markdown("### 🔊 Translated Audio")
                            audio_bytes = download_audio(result["translated_audio_url"])
                            if audio_bytes:
                                mime_type = get_audio_mime_type(result["translated_audio_url"])
                                st.audio(audio_bytes, format=mime_type)
                                
                                # Download button
                                st.download_button(
                                    label="📥 Download Audio",
                                    data=audio_bytes,
                                    file_name=f"translated_{target_lang}.mp3",
                                    mime=mime_type
                                )
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
        else:
            st.info("Enter text and click 'Process Text' to see results.")

# ============ AUDIO UPLOAD TAB ============
with tab2:
    st.header("Upload Audio File")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        audio_file = st.file_uploader(
            "Upload Audio",
            type=["mp3", "wav", "ogg", "m4a", "aac"],
            help="Maximum duration: 5 minutes"
        )
        
        audio_language = st.selectbox(
            "Translate to",
            options=list(LANGUAGES.keys()),
            index=0,
            key="audio_lang"
        )
        
        process_audio_btn = st.button("🔄 Process Audio", type="primary", use_container_width=True)
    
    with col2:
        if process_audio_btn:
            if audio_file is None:
                st.warning("Please upload an audio file.")
            else:
                # Save uploaded file to temp location
                with tempfile.NamedTemporaryFile(delete=False, suffix=Path(audio_file.name).suffix) as tmp_file:
                    tmp_file.write(audio_file.getvalue())
                    tmp_path = tmp_file.name
                
                try:
                    # Validate duration
                    is_valid, duration = validate_audio_duration(tmp_path)
                    if not is_valid:
                        st.error(f"❌ Audio file is too long ({duration:.1f} min). Maximum allowed is {MAX_AUDIO_MINUTES} minutes.")
                    else:
                        with st.spinner("Processing your audio... This may take a few minutes."):
                            try:
                                target_lang = LANGUAGES[audio_language]
                                result = pipeline.process_audio_input(tmp_path, target_lang)
                                
                                # Display results
                                st.success("✅ Processing complete!")
                                
                                st.markdown("### 📝 Transcript")
                                st.write(result["transcript"])
                                
                                st.markdown("### 📝 Summary")
                                st.write(result["summary"])
                                
                                st.markdown("### 🌐 Translated Summary")
                                st.write(result["translated_summary"])
                                
                                # Download and display audio
                                if result.get("translated_audio_url"):
                                    st.markdown("### 🔊 Translated Audio")
                                    audio_bytes = download_audio(result["translated_audio_url"])
                                    if audio_bytes:
                                        mime_type = get_audio_mime_type(result["translated_audio_url"])
                                        st.audio(audio_bytes, format=mime_type)
                                        
                                        # Download button
                                        st.download_button(
                                            label="📥 Download Audio",
                                            data=audio_bytes,
                                            file_name=f"translated_{target_lang}.mp3",
                                            mime=mime_type
                                        )
                            except Exception as e:
                                st.error(f"❌ Error: {str(e)}")
                finally:
                    # Clean up temp file
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)
        else:
            st.info("Upload an audio file and click 'Process Audio' to see results.")

# ============ FOOTER ============
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666;">
    <p>
        <strong>Powered by <a href="https://sunbird.ai" target="_blank">Sunbird AI</a> API</strong> | 
        Languages: Luganda, Runyankole, Acholi, Ateso, Lugbara | 
        Max audio: 5 minutes
    </p>
</div>
""", unsafe_allow_html=True)