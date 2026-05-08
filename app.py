"""
Main Gradio Application for Sunbird AI GenAI Pipeline
"""

import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv
import gradio as gr
from pathlib import Path
from backend.sunbird_client import SunbirdClient
from backend.pipeline import Pipeline
import tempfile
import requests

# Load .env file automatically from project root
from pathlib import Path
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# Load API token from environment
API_TOKEN = os.getenv("SUNBIRD_API_TOKEN")
if not API_TOKEN:
    print(f"ERROR: SUNBIRD_API_TOKEN not found.")
    print(f"Checked .env at: {env_path}")
    print("Create .env with: SUNBIRD_API_TOKEN=your_token")
    raise ValueError("SUNBIRD_API_TOKEN environment variable is required")

# Initialize client and pipeline
client = SunbirdClient(API_TOKEN)
pipeline = Pipeline(client)

# Language names for UI
LANGUAGES = {
    "Luganda": "lug",
    "Runyankole": "nyn",
    "Acholi": "ach",
    "Ateso": "teo",
    "Lugbara": "lgg"
}


def validate_audio_duration(audio_path: str, max_minutes: int = 5) -> tuple[bool, float]:
    """
    Check if audio file is within duration limit.
    Returns (is_valid, duration_in_minutes).
    """
    try:
        import librosa
        duration = librosa.get_duration(filename=audio_path)
        return duration <= (max_minutes * 60), duration / 60
    except ImportError:
        # Fallback: just accept (librosa not installed - user must handle)
        return True, 0.0
    except Exception:
        # If we can't determine, assume valid but warn
        return True, 0.0


def process_text_input(text_input: str, target_language_name: str) -> dict:
    """
    Handle text input mode.
    
    Returns:
        Dictionary with results or error
    """
    if not text_input or not text_input.strip():
        return {"error": "Please enter some text."}
    
    target_lang = LANGUAGES[target_language_name]
    
    try:
        result = pipeline.process_text_input(text_input.strip(), target_lang)
        return result
    except Exception as e:
        return {"error": str(e)}


def process_audio_input(audio_file, target_language_name: str) -> dict:
    """
    Handle audio upload mode.
    
    Returns:
        Dictionary with results or error
    """
    if audio_file is None:
        return {"error": "Please upload an audio file."}
    
    audio_path = audio_file if isinstance(audio_file, str) else audio_file.name
    
    # Validate duration (5 min max)
    is_valid, duration = validate_audio_duration(audio_path, 5)
    if not is_valid:
        return {"error": f"Audio file is too long ({duration:.1f} min). Maximum allowed is 5 minutes."}
    
    target_lang = LANGUAGES[target_language_name]
    
    try:
        result = pipeline.process_audio_input(audio_path, target_lang)
        result["audio_duration_min"] = duration
        return result
    except Exception as e:
        return {"error": str(e)}


def download_audio(audio_url: str) -> Optional[str]:
    """Download audio from URL and return local temp file path."""
    try:
        response = requests.get(audio_url, stream=True)
        response.raise_for_status()
        
        # Create temp file
        suffix = Path(audio_url).suffix or ".mp3"
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        temp_file.write(response.content)
        temp_file.close()
        
        return temp_file.name
    except Exception as e:
        print(f"Failed to download audio: {e}")
        return None


# Gradio Interface
with gr.Blocks(title="Sunbird AI Voice Translator", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🌍 Sunbird AI Voice Translator")
    gr.Markdown("""
    Transform your voice or text into summaries, then translate and speak them in Ugandan languages.
    
    **Pipeline:** Input → Transcribe (audio only) → Summarize → Translate → Speech
    """)
    
    with gr.Tabs() as tabs:
        # ============ TEXT INPUT TAB ============
        with gr.TabItem("✍️ Text Input", id=0):
            gr.Markdown("Enter your text and choose a target language.")
            
            with gr.Row():
                with gr.Column(scale=2):
                    text_input = gr.Textbox(
                        label="Your Text",
                        placeholder="Type or paste your text here...",
                        lines=6,
                        max_lines=10
                    )
                    
                    text_language = gr.Dropdown(
                        choices=list(LANGUAGES.keys()),
                        value="Luganda",
                        label="Translate to"
                    )
                    
                    text_submit_btn = gr.Button("🔄 Process Text", variant="primary")
                
                with gr.Column(scale=3):
                    gr.Markdown("### Results")
                    
                    text_output_summary = gr.Textbox(
                        label="📝 Summary",
                        lines=4,
                        interactive=False
                    )
                    
                    text_output_translated = gr.Textbox(
                        label="🌐 Translated Summary",
                        lines=4,
                        interactive=False
                    )
                    
                    text_output_audio = gr.Audio(
                        label="🔊 Translated Audio",
                        type="filepath"
                    )
                    
                    text_error = gr.Textbox(
                        label="Status / Errors",
                        interactive=False,
                        lines=2
                    )
        
        # ============ AUDIO INPUT TAB ============
        with gr.TabItem("🎙️ Audio Upload", id=1):
            gr.Markdown("""
            Upload an audio file (max 5 minutes). The app will:
            1. Transcribe your audio
            2. Summarize the transcript
            3. Translate the summary
            4. Generate spoken audio of the translation
            """)
            
            with gr.Row():
                with gr.Column(scale=2):
                    audio_input = gr.Audio(
                        label="Upload Audio",
                        type="filepath",
                        sources=["upload"]
                    )
                    
                    audio_language = gr.Dropdown(
                        choices=list(LANGUAGES.keys()),
                        value="Luganda",
                        label="Translate to"
                    )
                    
                    audio_submit_btn = gr.Button("🔄 Process Audio", variant="primary")
                
                with gr.Column(scale=3):
                    gr.Markdown("### Results")
                    
                    audio_output_transcript = gr.Textbox(
                        label="📝 Transcript",
                        lines=4,
                        interactive=False
                    )
                    
                    audio_output_summary = gr.Textbox(
                        label="📝 Summary",
                        lines=4,
                        interactive=False
                    )
                    
                    audio_output_translated = gr.Textbox(
                        label="🌐 Translated Summary",
                        lines=4,
                        interactive=False
                    )
                    
                    audio_output_speech = gr.Audio(
                        label="🔊 Translated Audio",
                        type="filepath"
                    )
                    
                    audio_error = gr.Textbox(
                        label="Status / Errors",
                        interactive=False,
                        lines=2
                    )
    
    # ============ FOOTER ============
    gr.Markdown("---")
    gr.Markdown("""
    **Powered by [Sunbird AI](https://sunbird.ai) API** | 
    Languages: Luganda, Runyankole, Acholi, Ateso, Lugbara | 
    Max audio: 5 minutes
    """)
    
    # ============ EVENT HANDLERS ============
    from typing import Optional  # Ensure Optional is in scope
    
    def handle_text_submit(text, lang_name):
        """Process text input and return all outputs."""
        if not text or not text.strip():
            return "", "", None, "Please enter some text."
        
        result = process_text_input(text, lang_name)
        
        if "error" in result:
            return "", "", None, f"❌ Error: {result['error']}"
        
        # Download audio for playback
        audio_url = result["translated_audio_url"]
        local_audio = None
        if audio_url:
            local_audio = download_audio(audio_url)
        
        return (
            result["summary"],
            result["translated_summary"],
            local_audio,
            "✅ Processing complete!"
        )
    
    def handle_audio_submit(audio_path, lang_name):
        """Process audio input and return all outputs."""
        result = process_audio_input(audio_path, lang_name)
        
        if "error" in result:
            return "", "", "", None, f"❌ Error: {result['error']}"
        
        # Download audio for playback
        audio_url = result["translated_audio_url"]
        local_audio = None
        if audio_url:
            local_audio = download_audio(audio_url)
        
        return (
            result["transcript"],
            result["summary"],
            result["translated_summary"],
            local_audio,
            "✅ Processing complete!"
        )
    
    text_submit_btn.click(
        fn=handle_text_submit,
        inputs=[text_input, text_language],
        outputs=[text_output_summary, text_output_translated, text_output_audio, text_error]
    )
    
    audio_submit_btn.click(
        fn=handle_audio_submit,
        inputs=[audio_input, audio_language],
        outputs=[audio_output_transcript, audio_output_summary, audio_output_translated, 
                audio_output_speech, audio_error]
    )


if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False  # Set to True for temporary public link
    )
