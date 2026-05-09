# Sunbird AI Voice Translator

A Generative AI web app that transforms voice or text into summarized, translated speech in Ugandan languages. Built with **Streamlit**, Python, and the Sunbird AI API.

## Project Description .

This application enables users to either speak or type content, then automatically:
- **Transcribe** audio using Sunbird's Speech-to-Text (STT) model
- **Summarize** the transcript using Sunflower LLM
- **Translate** the summary to Luganda, Runyankole, Acholi, Ateso, or Lugbara
- **Synthesize speech** of the translated summary using Text-to-Speech (TTS)

The pipeline serves as a voice-enabled multilingual assistant for Ugandan languages, enabling accessibility and cross-language communication.

## Architecture Overview

```
┌─────────────────┐
│   User Input    │
│  ┌───────────┐  │
│  │ Text OR   │  │
│  │ Audio     │  │
│  └─────┬─────┘  │
│        │        │
│        ▼        │
│  ┌───────────┐  │
│  │  STT API  │◄─┼─ Audio path only
│  │ /tasks/   │  │
│  │ modal/stt │  │ Produces: transcript
│  └─────┬─────┘  │
│        │        │
│        ▼        │
│  ┌───────────┐  │
│  │ Sunflower │  │
│  │Inference  │  │ Produces: summary
│  └─────┬─────┘  │
│        │        │
│        ▼        │
│  ┌───────────┐  │
│  │ Sunflower │  │ Produces: translation
│  │Inference  │  │
│  └─────┬─────┘  │
│        │        │
│        ▼        │
│  ┌───────────┐  │
│  │  TTS API  │  │
│  │ /tasks/   │  │ Produces: audio_url
│  │ modal/tts │  │
│  └─────┬─────┘  │
│        │        │
│        ▼        │
│  ┌───────────┐  │
│  │  Output   │  │
│  │• Original │  │
│  │• Summary  │  │
│  │• Translated│ │
│  │• Audio    │  │
│  └───────────┘  │
└─────────────────┘
```

**API Endpoints used:**
| Step | Endpoint | Purpose |
|------|----------|---------|
| STT | `POST /tasks/modal/stt` | Transcribes audio → text |
| Summarize | `POST /tasks/sunflower_inference` | Generates concise summary |
| Translate | `POST /tasks/sunflower_inference` | Translates to target language |
| TTS | `POST /tasks/modal/tts` | Generates spoken audio file |

**Project structure:**
```
.
├── app.py                      # Streamlit UI entry point
├── backend/
│   ├── __init__.py
│   ├── sunbird_client.py       # API client wrapper
│   └── pipeline.py             # Orchestrates STT → Summary → Translate → TTS
├── exercises/
│   ├── __init__.py
│   └── basics.py               # Programming exercises
├── tests/
│   ├── __init__.py
│   └── test_basics.py          # Unit tests
├── .env.example                # Environment template
├── .gitignore                  # Git ignore file
├── constants.py                # Test constants
├── requirements.txt            # Python dependencies
└── README.md                   # Internship assessment instructions
```

## Local Setup

### Prerequisites
- Python 3.9+ installed
- Git installed

### Step-by-Step Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/<your-username>/internship-assessment.git
   cd internship-assessment
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   - Copy `.env.example` to `.env`
   - Replace `your_access_token_here` with your actual Sunbird AI API token
   
   ```bash
   copy .env.example .env
   ```
   
   **Get your token:** Sign up at [api.sunbird.ai](https://api.sunbird.ai), then generate an access token in your account dashboard.

5. **Run the application**
   ```bash
   streamlit run app.py
   ```
   
   The app will start at: `http://localhost:8501`

6. **Open in browser**
   Navigate to `http://localhost:8501` to use the app.

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SUNBIRD_API_TOKEN` | Your Sunbird AI access token from https://api.sunbird.ai | Yes |

**Security note:** Never commit your `.env` file. The `.gitignore` already excludes it.

## Usage

### Text Input Mode

1. Click on the **"✍️ Text Input"** tab
2. Type or paste your text (e.g., a paragraph of news or a story)
3. Choose your target language (Luganda, Runyankole, Acholi, Ateso, or Lugbara)
4. Click **"🔄 Process Text"**
5. View the summary, translated summary, and listen to the audio

Example walkthrough:
```
Input:  "The African Union announced a new climate resilience initiative..."
Target: Luganda
→ Summary: "The AU launched a climate initiative to improve resilience..."
→ Translation: "Awaka olukasa lw'obuyinza bw'Afrika..."
→ Audio: Play button appears with download option
```

### Audio Upload Mode

1. Click on the **"🎙️ Audio Upload"** tab
2. Upload an MP3, WAV, OGG, M4A, or AAC file (max 5 minutes)
3. Choose your target language
4. Click **"🔄 Process Audio"**
5. View the transcript, summary, translated summary, and listen to the audio

Example flow:
```
Upload: "recording.mp3" (1 min 12 sec)
Target: Runyankole
→ Transcript: "We are gathered here to discuss..."
→ Summary: "The speaker discussed a community gathering..."
→ Translation: "Turi kuhikiriza aha...".
→ Audio: Playable and downloadable MP3
```

### Language Options

| Language | Code | Notes |
|----------|------|-------|
| Luganda | `lug` | Most widely supported |
| Runyankole | `nyn` | Popular in Western Uganda |
| Acholi | `ach` | Northern Uganda |
| Ateso | `teo` | Eastern Uganda |
| Lugbara | `lgg` | Northern/Western Uganda |

## Known Limitations

1. **Audio duration:** Rejects files longer than 5 minutes (the Sunbird API supports up to 10 min, but this app enforces 5 min). Longer files must be split.
2. **Audio formats:** MP3, WAV, OGG, M4A, AAC are supported by Sunbird.
3. **Token expiry:** Sunbird access tokens last 7 days. If requests fail with 401, refresh your token.
4. **Rate limiting:** The API imposes rate limits; concurrent users may be throttled.
5. **Internet required:** All processing happens via cloud API; no offline mode.
6. **Audio storage:** TTS returns a temporary signed URL (valid ~30 minutes). Download promptly.

## Deployment

The app is deployed on **Streamlit Cloud** for free hosting.

### Deploy to Streamlit Cloud

1. **Push your code to GitHub**

2. **Go to** https://streamlit.io/cloud

3. **Sign in** with your GitHub account

4. **Click "Deploy an app"** and select your repository

5. **Add environment variables** in Streamlit Cloud settings:
   - Go to app Settings → Secrets
   - Add secret: `SUNBIRD_API_TOKEN` = `<your-token>`

6. **Deploy!** The app will be live in minutes.

**Deployed URL:** [https://sunbird-assistant.streamlit.app/](https://sunbird-assistant.streamlit.app/)

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `SUNBIRD_API_TOKEN not found` | Ensure `.env` file exists with correct variable, or set as HF Space secret |
| Audio too long error | Trim audio to under 5 minutes before upload |
| 401 Unauthorized | Refresh your Sunbird API token |
| 422 Validation Error | Check that target language is supported |
| Streamlit fails to start | Verify port 8501 is available |
| Audio doesn't play | Wait for download to complete; check URL expiry |
| librosa import error | Ensure soundfile or audioread is installed: `pip install soundfile` |

### Debug mode

Set `STREAMLIT_LOG_LEVEL=debug` to see detailed logs:
```bash
set STREAMLIT_LOG_LEVEL=debug  # Windows
export STREAMLIT_LOG_LEVEL=debug  # macOS/Linux
streamlit run app.py
```

## Running Tests

The project includes programming exercises with unit tests:

```bash
# Install dev dependencies
pip install pytest

# Run tests
pytest
```

## Contributing

This project is part of the Sunbird AI Internship Assessment. Code should follow PEP 8 and type hints are encouraged.

## License

This project is provided as-is for assessment purposes only.