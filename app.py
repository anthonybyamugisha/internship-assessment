"""
Sunbird AI Voice Translator - Professional Streamlit Application
Enhanced with modern design and professional UI/UX
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
import time
from datetime import datetime

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

# Custom CSS for professional styling
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@600;700&display=swap');
    
    /* Global Styles */
    .stApp {
        font-family: 'Inter', sans-serif;
    }
    
    /* Header Styling */
    .main-header {
        font-family: 'Playfair Display', serif;
        font-size: 3rem;
        font-weight: 700;
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem;
        padding: 2rem 0 1rem 0;
    }
    
    .sub-header {
        font-size: 1.2rem;
        text-align: center;
        color: #4a5568;
        margin-bottom: 2.5rem;
        font-weight: 300;
        line-height: 1.6;
    }
    
    /* Card Styling */
    .result-card {
        background: linear-gradient(135deg, #ffffff 0%, #f7fafc 100%);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05), 0 10px 15px rgba(0, 0, 0, 0.1);
        border: 1px solid #e2e8f0;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .result-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
    }
    
    .card-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #2d3748;
        margin-bottom: 0.75rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .card-content {
        font-size: 0.95rem;
        line-height: 1.6;
        color: #4a5568;
    }
    
    /* Button Styling */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 12px;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
    }
    
    /* Input Styling */
    .stTextInput>div>div>input,
    .stTextArea>div>div>textarea {
        border-radius: 12px;
        border: 2px solid #e2e8f0;
        padding: 1rem;
        font-size: 1rem;
        transition: border-color 0.3s ease;
    }
    
    .stTextInput>div>div>input:focus,
    .stTextArea>div>div>textarea:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Select Box Styling */
    .stSelectbox>div>div>select {
        border-radius: 10px;
        border: 2px solid #e2e8f0;
        padding: 0.75rem 1rem;
        font-size: 0.95rem;
    }
    
    /* Success/Error Messages */
    .success-message {
        background: linear-gradient(135deg, #c6f6d5 0%, #9ae6b4 100%);
        padding: 1rem 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        border-left: 4px solid #48bb78;
        font-weight: 500;
    }
    
    .error-message {
        background: linear-gradient(135deg, #fed7d7 0%, #feb2b2 100%);
        padding: 1rem 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        border-left: 4px solid #f56565;
        font-weight: 500;
    }
    
    /* Info Box */
    .info-box {
        background: linear-gradient(135deg, #bee3f8 0%, #90cdf4 100%);
        padding: 1rem 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        border-left: 4px solid #4299e1;
    }
    
    /* Sidebar Styling */
    .sidebar-content {
        padding: 1rem;
    }
    
    .sidebar-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: #2d3748;
        margin-bottom: 1rem;
    }
    
    /* Progress Animation */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .processing {
        animation: pulse 2s infinite;
    }
    
    /* Divider */
    .custom-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, #e2e8f0, transparent);
        margin: 2rem 0;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem 0;
        color: #718096;
        font-size: 0.9rem;
        margin-top: 3rem;
    }
    
    /* Language Badge */
    .language-badge {
        display: inline-block;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 500;
        margin: 0.25rem;
    }
    
    /* Stats Card */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .stat-card {
        background: white;
        padding: 1rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .stat-number {
        font-size: 1.5rem;
        font-weight: 700;
        color: #667eea;
    }
    
    .stat-label {
        font-size: 0.85rem;
        color: #718096;
        margin-top: 0.25rem;
    }
</style>
""", unsafe_allow_html=True)

# Load API token from environment
API_TOKEN = os.getenv("SUNBIRD_API_TOKEN")
if not API_TOKEN:
    st.markdown("""
    <div class="error-message">
        <h3>❌ Missing API Token</h3>
        <p>The <code>SUNBIRD_API_TOKEN</code> environment variable is not set.</p>
        <p><strong>To fix this:</strong></p>
        <ol>
            <li>Create a <code>.env</code> file in the project directory</li>
            <li>Add: <code>SUNBIRD_API_TOKEN=your_token_here</code></li>
            <li>Or set it as a secret in Streamlit Cloud / Hugging Face Spaces</li>
        </ol>
        <p>Get your token from: <a href="https://api.sunbird.ai/" target="_blank">https://api.sunbird.ai/</a></p>
    </div>
    """, unsafe_allow_html=True)
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


def display_result_card(title: str, content: str, icon: str = "📝"):
    """Display a styled result card."""
    st.markdown(f"""
    <div class="result-card">
        <div class="card-title">{icon} {title}</div>
        <div class="card-content">{content}</div>
    </div>
    """, unsafe_allow_html=True)


# ============ MAIN UI ============
st.markdown('<h1 class="main-header">🌍 Sunbird AI Voice Translator</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Transform your voice or text into intelligent summaries, then translate and speak them in Ugandan languages with the power of AI.</p>', unsafe_allow_html=True)

# Sidebar with enhanced styling
with st.sidebar:
    st.markdown("""
    <div class="sidebar-content">
        <div class="sidebar-title">ℹ️ About This App</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    This application leverages **Sunbird AI's** advanced models to provide:
    
    🎯 **Accurate Transcription** - Convert speech to text  
    📝 **Intelligent Summarization** - Extract key points  
    🌐 **Multi-language Translation** - Support for 5 Ugandan languages  
    🔊 **Natural Speech Synthesis** - High-quality audio generation
    """)
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    st.markdown("### 🗣️ Supported Languages")
    for lang_name, lang_code in LANGUAGES.items():
        st.markdown(f'<span class="language-badge">{lang_name}</span>', unsafe_allow_html=True)
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    st.info("📝 **Note:** Audio files must be under 5 minutes for processing.")
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; margin-top: 1rem;">
        <p style="font-size: 0.85rem; color: #718096;">
            <strong>Powered by</strong><br>
            <a href="https://sunbird.ai" target="_blank" style="color: #667eea; text-decoration: none;">
                Sunbird AI
            </a>
        </p>
    </div>
    """, unsafe_allow_html=True)

# Main content area with tabs
tab1, tab2 = st.tabs(["✍️ Text Input", "🎙️ Audio Upload"])

# ============ TEXT INPUT TAB ============
with tab1:
    st.markdown("### Enter Your Text")
    st.markdown("Type or paste your content below, select a target language, and let our AI transform it.")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        text_input = st.text_area(
            "Your Text",
            placeholder="Type or paste your text here... (e.g., news article, story, document)",
            height=250,
            label_visibility="collapsed"
        )
        
        target_language = st.selectbox(
            "🌐 Target Language",
            options=list(LANGUAGES.keys()),
            index=0,
            label_visibility="collapsed"
        )
        
        process_text_btn = st.button("🚀 Process Text", type="primary", use_container_width=True)
    
    with col2:
        if process_text_btn:
            if not text_input or not text_input.strip():
                st.warning("⚠️ Please enter some text to process.")
            else:
                # Create progress placeholder
                progress_container = st.empty()
                status_container = st.empty()
                
                try:
                    start_time = time.time()
                    target_lang = LANGUAGES[target_language]
                    
                    # Show progress steps
                    progress_container.progress(0)
                    status_container.info("🔄 Step 1/4: Summarizing text...")
                    
                    # Step 1: Summarize
                    summary = pipeline.client.summarize_text(text_input.strip())
                    progress_container.progress(33)
                    status_container.info("🔄 Step 2/4: Translating to " + target_language + "...")
                    
                    # Step 2: Translate
                    translated = pipeline.client.translate_text(summary, target_lang)
                    progress_container.progress(66)
                    status_container.info("🔄 Step 3/4: Generating speech audio...")
                    
                    # Step 3: Synthesize speech
                    audio_url = pipeline.client.synthesize_speech(translated, target_lang)
                    progress_container.progress(100)
                    status_container.success("✅ Processing complete!")
                    
                    processing_time = time.time() - start_time
                    
                    # Clear progress indicators after a moment
                    time.sleep(0.5)
                    progress_container.empty()
                    status_container.empty()
                    
                    result = {
                        "summary": summary,
                        "translated_summary": translated,
                        "translated_audio_url": audio_url
                    }
                    
                    # Display success message
                    st.markdown(f"""
                    <div class="success-message">
                        ✅ Processing complete! ({processing_time:.1f}s)
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Display results in cards
                    display_result_card("📝 Summary", result["summary"], "")
                    display_result_card("🌐 Translated Summary", result["translated_summary"], "")
                    
                    # Audio section
                    if result.get("translated_audio_url"):
                        st.markdown("### 🔊 Translated Audio")
                        audio_bytes = download_audio(result["translated_audio_url"])
                        if audio_bytes:
                            mime_type = get_audio_mime_type(result["translated_audio_url"])
                            st.audio(audio_bytes, format=mime_type)
                            
                            # Download button
                            st.download_button(
                                label="📥 Download Audio File",
                                data=audio_bytes,
                                file_name=f"translated_{target_lang}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3",
                                mime=mime_type,
                                use_container_width=True
                            )
                    
                    # Processing stats
                    with st.expander("📊 Processing Statistics"):
                        st.markdown(f"""
                        <div class="stats-grid">
                            <div class="stat-card">
                                <div class="stat-number">{len(text_input)}</div>
                                <div class="stat-label">Characters</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-number">{len(result['summary'])}</div>
                                <div class="stat-label">Summary Chars</div>
                            </div>
                            <div class="stat-card">
                                <div class="stat-number">{processing_time:.1f}s</div>
                                <div class="stat-label">Processing Time</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                except Exception as e:
                    progress_container.empty()
                    status_container.empty()
                    st.markdown(f"""
                    <div class="error-message">
                        ❌ Error: {str(e)}
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="info-box">
                💡 <strong>Tip:</strong> Enter text and click 'Process Text' to see the AI-generated summary, translation, and audio.
            </div>
            """, unsafe_allow_html=True)

# ============ AUDIO UPLOAD TAB ============
with tab2:
    st.markdown("### Upload Audio File")
    st.markdown("Upload an audio recording and our AI will transcribe, summarize, translate, and generate speech in your chosen language.")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        audio_file = st.file_uploader(
            "Upload Audio File",
            type=["mp3", "wav", "ogg", "m4a", "aac"],
            help="Supported formats: MP3, WAV, OGG, M4A, AAC (Max 5 minutes)",
            label_visibility="collapsed"
        )
        
        audio_language = st.selectbox(
            "🌐 Target Language",
            options=list(LANGUAGES.keys()),
            index=0,
            key="audio_lang",
            label_visibility="collapsed"
        )
        
        process_audio_btn = st.button("🚀 Process Audio", type="primary", use_container_width=True)
    
    with col2:
        if process_audio_btn:
            if audio_file is None:
                st.warning("⚠️ Please upload an audio file to process.")
            else:
                # Save uploaded file to temp location
                with tempfile.NamedTemporaryFile(delete=False, suffix=Path(audio_file.name).suffix) as tmp_file:
                    tmp_file.write(audio_file.getvalue())
                    tmp_path = tmp_file.name
                
                try:
                    # Validate duration
                    is_valid, duration = validate_audio_duration(tmp_path)
                    if not is_valid:
                        st.markdown(f"""
                        <div class="error-message">
                            ❌ Audio file is too long ({duration:.1f} minutes). Maximum allowed is {MAX_AUDIO_MINUTES} minutes.
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        # Create progress placeholder
                        progress_container = st.empty()
                        status_container = st.empty()
                        
                        try:
                            start_time = time.time()
                            target_lang = LANGUAGES[audio_language]
                            
                            # Show progress steps
                            progress_container.progress(0)
                            status_container.info("🔄 Step 1/4: Transcribing audio...")
                            
                            # Step 1: Transcribe
                            transcript = pipeline.client.transcribe_audio(tmp_path)
                            progress_container.progress(25)
                            status_container.info("🔄 Step 2/4: Summarizing transcript...")
                            
                            # Step 2: Summarize
                            summary = pipeline.client.summarize_text(transcript)
                            progress_container.progress(50)
                            status_container.info("🔄 Step 3/4: Translating to " + audio_language + "...")
                            
                            # Step 3: Translate
                            translated = pipeline.client.translate_text(summary, target_lang)
                            progress_container.progress(75)
                            status_container.info("🔄 Step 4/4: Generating speech audio...")
                            
                            # Step 4: Synthesize speech
                            audio_url = pipeline.client.synthesize_speech(translated, target_lang)
                            progress_container.progress(100)
                            status_container.success("✅ Processing complete!")
                            
                            processing_time = time.time() - start_time
                            
                            # Clear progress indicators after a moment
                            time.sleep(0.5)
                            progress_container.empty()
                            status_container.empty()
                            
                            result = {
                                "transcript": transcript,
                                "summary": summary,
                                "translated_summary": translated,
                                "translated_audio_url": audio_url
                            }
                            
                            # Display success message
                            st.markdown(f"""
                            <div class="success-message">
                                ✅ Processing complete! ({processing_time:.1f}s)
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Display all results
                            display_result_card("📝 Transcript", result["transcript"], "")
                            display_result_card("📝 Summary", result["summary"], "")
                            display_result_card("🌐 Translated Summary", result["translated_summary"], "")
                            
                            # Audio section
                            if result.get("translated_audio_url"):
                                st.markdown("### 🔊 Translated Audio")
                                audio_bytes = download_audio(result["translated_audio_url"])
                                if audio_bytes:
                                    mime_type = get_audio_mime_type(result["translated_audio_url"])
                                    st.audio(audio_bytes, format=mime_type)
                                    
                                    # Download button
                                    st.download_button(
                                        label="📥 Download Audio File",
                                        data=audio_bytes,
                                        file_name=f"translated_{target_lang}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3",
                                        mime=mime_type,
                                        use_container_width=True
                                    )
                            
                            # Processing stats
                            with st.expander("📊 Processing Statistics"):
                                st.markdown(f"""
                                <div class="stats-grid">
                                    <div class="stat-card">
                                        <div class="stat-number">{duration:.1f}s</div>
                                        <div class="stat-label">Audio Duration</div>
                                    </div>
                                    <div class="stat-card">
                                        <div class="stat-number">{len(result['transcript'])}</div>
                                        <div class="stat-label">Transcript Chars</div>
                                    </div>
                                    <div class="stat-card">
                                        <div class="stat-number">{processing_time:.1f}s</div>
                                        <div class="stat-label">Processing Time</div>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                                
                        except Exception as e:
                            progress_container.empty()
                            status_container.empty()
                            st.markdown(f"""
                            <div class="error-message">
                                ❌ Error: {str(e)}
                            </div>
                            """, unsafe_allow_html=True)
                finally:
                    # Clean up temp file
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)
        else:
            st.markdown("""
            <div class="info-box">
                🎙️ <strong>Ready:</strong> Upload an audio file and click 'Process Audio' to begin transcription, summarization, and translation.
            </div>
            """, unsafe_allow_html=True)

# ============ FOOTER ============
st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
st.markdown("""
<div class="footer">
    <p>
        <strong>🌍 Sunbird AI Voice Translator</strong> | 
        Powered by <a href="https://sunbird.ai" target="_blank" style="color: #667eea; text-decoration: none;">Sunbird AI</a> API | 
        Languages: Luganda, Runyankole, Acholi, Ateso, Lugbara | 
        Max audio: 5 minutes
    </p>
    <p style="font-size: 0.8rem; margin-top: 0.5rem; color: #a0aec0;">
        © 2024 Sunbird AI Internship Assessment. Built with ❤️ using Streamlit.
    </p>
</div>
""", unsafe_allow_html=True)