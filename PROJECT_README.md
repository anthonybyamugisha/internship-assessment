# Sunbird AI Voice Translator

A Generative AI web app that transforms voice or text into summarized, translated speech in Ugandan languages. Built with Gradio, Python, and the Sunbird AI API.

## Project Description

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
│  │  Simple   │  │ Produces: summary
│  │Inference  │  │
│  └─────┬─────┘  │
│        │        │
│        ▼        │
│  ┌───────────┐  │
│  │ Sunflower │  │ Produces: translation
│  │  Simple   │  │
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
| Summarize | `POST /tasks/sunflower_simple` | Generates concise summary |
| Translate | `POST /tasks/sunflower_simple` | Translates to target language |
| TTS | `POST /tasks/modal/tts` | Generates spoken audio file |

**Project structure:**
```
.
├── app.py                      # Gradio UI entry point
├── backend/
│   ├── sunbird_client.py       # API client wrapper
│   └── pipeline.py             # Orchestrates STT → Summary → Translate → TTS
├── .env.example                # Environment template
├── requirements.txt            # Python dependencies
└── README.md                  # This file
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
   python app.py
   ```
   
   The app will start at: `http://localhost:7860`

6. **Open in browser**
   Navigate to `http://localhost:7860` to use the app.

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SUNBIRD_API_TOKEN` | Your Sunbird AI access token from https://api.sunbird.ai | Yes |

**Security note:** Never commit your `.env` file. The `.gitignore` already excludes it.

## Usage

### Text Input Mode

1. Select the **"✍️ Text Input"** tab
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
→ Audio: Play button appears
```

### Audio Upload Mode

1. Select the **"🎙️ Audio Upload"** tab
2. Upload an MP3, WAV, or M4A file (max 5 minutes)
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
→ Audio: Downloadable MP3
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

The app is deployed on **Hugging Face Spaces** for free hosting.

### Deploy to Hugging Face Spaces (recommended)

1. Create a Hugging Face account: https://huggingface.co/join
2. Create new Space: https://huggingface.co/new-space
   - Select **Gradio** SDK
   - Choose **Public** visibility
   - Name your space (e.g., `sunbird-voice-translator`)
3. Add your Sunbird API token as a secret:
   - Go to Space Settings → **Variables and secrets**
   - Add secret: `SUNBIRD_API_TOKEN` = `<your-token>`
4. Push your code:
   ```bash
   git remote add space https://huggingface.co/spaces/<your-username>/<your-space-name>
   git push space main
   ```
5. Hugging Face builds and deploys automatically (~2-5 min)

**Deployed URL:** [https://huggingface.co/spaces/](https://huggingface.co/spaces/) (you'll need to add your own)

### Alternative: Vercel (for Next.js frontend + Python backend)

If you extend this to a custom frontend later, Vercel is an option. See the internship instructions for guidance.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `SUNBIRD_API_TOKEN not found` | Ensure `.env` file exists with correct variable |
| Audio too long error | Trim audio to under 5 minutes before upload |
| 401 Unauthorized | Refresh your Sunbird API token |
| 422 Validation Error | Check that target language is supported |
| Gradio fails to start | Verify port 7860 is available |
| Audio doesn't play | Wait for download to complete; check URL expiry |

### Debug mode

Set `GRADIO_DEBUG=true` in `.env` to see detailed logs:
```bash
set GRADIO_DEBUG=true  # Windows
export GRADIO_DEBUG=true  # macOS/Linux
python app.py
```

## Contributing

This project is part of the Sunbird AI Internship Assessment. Code should follow PEP 8 and type hints are encouraged.

## License

This project is provided as-is for assessment purposes only.
