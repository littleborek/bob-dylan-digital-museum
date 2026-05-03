# 🎸 Bob Dylan AI Portal

A multi-layered AI portal that brings Bob Dylan to life — visually, intellectually, and vocally — using cutting-edge AI technologies.

![Dylan AI](https://img.shields.io/badge/Dylan-AI-c4983a?style=for-the-badge) ![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge) ![UE5](https://img.shields.io/badge/Unreal_Engine-5.6.1-black?style=for-the-badge)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    BROWSER (Frontend)                        │
│  ┌─────────────────┐  ┌──────────────────────────────────┐  │
│  │  Pixel Streaming │  │         Chat Panel               │  │
│  │  (iframe → UE5)  │  │  Text + Voice input → AI reply   │  │
│  │  Press T to talk │  │                                  │  │
│  └─────────────────┘  └──────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐│
│  │              Dylan Lens Gallery                           ││
│  │  Random pre-loaded images • Shuffle to explore           ││
│  │  LLaVA interpretation → ComfyUI vintage reimagining      ││
│  └──────────────────────────────────────────────────────────┘│
└──────────────┬──────────────────────────┬───────────────────┘
               │                          │
        ┌──────▼──────┐           ┌───────▼───────┐
        │  main.py    │           │ gallery_server │
        │  Port 8000  │           │   Port 8002    │
        │  Chat API   │           │  Gallery API   │
        └──────┬──────┘           └───────┬───────┘
               │                          │
    ┌──────────▼──────────┐    ┌──────────▼──────────┐
    │   LangGraph Agent   │    │     LLaVA (Vision)  │
    │   + RAG + Wikipedia │    │     + ComfyUI (SD)  │
    │   (Mistral Nemo)    │    │                     │
    └──────────┬──────────┘    └─────────────────────┘
               │
    ┌──────────▼──────────┐    ┌─────────────────────┐
    │   XTTS v2 (TTS)    │───▶│   UE Bridge (8500)  │
    │   Port 8001         │    │   → Lip Sync WAV    │
    │   Dylan Voice Clone │    │   → Audio2Face 3    │
    └─────────────────────┘    │   → MetaHuman Rig   │
                               └─────────────────────┘
```

---

## ✨ Features

### 🤖 AI Chatbot
- **Brain:** LangGraph agent with RAG (ChromaDB) + Wikipedia search
- **LLM:** Mistral Nemo Instruct (via LM Studio)
- **Voice:** XTTS v2 voice cloning — speaks in Dylan's voice
- **3D Character:** MetaHuman Rig in Unreal Engine 5.6.1 via Pixel Streaming
- **Facial Animation:** NVIDIA Audio2Face 3 driving MetaHuman AnimBPMH workflow
- **Keyboard Shortcut:** Press **T** to talk to the 3D Bob Dylan character

### 🎨 Dylan Lens Gallery
- **Instant loading:** 4 random pre-processed images displayed on page load — no waiting
- **Shuffle button:** Click to get a fresh random set of images from the archive
- **LLaVA** interprets each image with a poetic Dylan-style quote
- **ComfyUI (Stable Diffusion)** reimagines photos in 1960s vintage style
- Hover over any card to reveal the "Dylan Lens" reimagined version

### 🎙️ Voice Input
- Record voice messages via browser microphone
- Whisper STT transcription → AI response → Dylan voice reply

---

## 📁 Project Structure

```
bob-dylan/
├── main.py                 # Chat backend (FastAPI, port 8000)
├── agent.py                # LangGraph agent (Mistral Nemo + tools)
├── rag.py                  # RAG / ChromaDB vector store
├── stt_service.py          # Whisper speech-to-text
├── tts_server.py           # XTTS v2 voice server (port 8001)
├── gallery_server.py       # Gallery backend (FastAPI, port 8002)
├── ue_bridge.py            # UE audio bridge (port 8500)
├── dylan_ref.wav           # Dylan voice reference for cloning
├── .env                    # API keys & service URLs
├── gallery-frontend/       # Web frontend
│   ├── index.html
│   ├── main.css
│   └── main.js
├── chroma_db/              # Vector database
├── data/                   # Dylan knowledge base
├── generated_audio/        # TTS output WAV files
├── gallery_images/         # Downloaded & processed gallery images
├── tts_server_venv/        # Python 3.11 venv for XTTS
└── Bob-Dylan-artroom/      # 3D artroom assets
```

---

## 🚀 Quick Start

### Prerequisites
- **macOS** with Python 3.12 + `uv` package manager
- **Remote GPU machine** (Tailscale VPN) running:
  - LM Studio (Mistral Nemo + LLaVA models)
  - ComfyUI (Stable Diffusion)
  - Unreal Engine 5.6.1 (Pixel Streaming, MetaHuman, Audio2Face 3)

### 1. Configure Environment
```bash
cp .env.example .env
# Edit .env with your IPs and API keys
```

`.env` variables:
```env
LMSTUDIO_BASE=http://<GPU_MACHINE_IP>:1234
LMSTUDIO_MODEL=llava-1.6-mistral-7b
COMFYUI_BASE=http://<GPU_MACHINE_IP>:8188
GOOGLE_API_KEY=<optional>
GOOGLE_CSE_ID=<optional>
```

### 2. Start Services (4 Terminals)

```bash
# Terminal 1: TTS Voice Server (Python 3.11 venv)
./tts_server_venv/bin/python tts_server.py

# Terminal 2: Chat Backend
uv run uvicorn main:app --host 0.0.0.0 --port 8000

# Terminal 3: Gallery Backend + Frontend
uv run uvicorn gallery_server:app --host 0.0.0.0 --port 8002

# Terminal 4 (on UE machine): Audio Bridge
python3 ue_bridge.py
```

### 3. Open in Browser
```
http://localhost:8002
```

For Tailscale access from other devices:
```
http://<YOUR_TAILSCALE_IP>:8002
```

---

## 🎮 Controls

| Key / Action | Description |
|-------------|-------------|
| **T** | Talk to the 3D Bob Dylan character (Pixel Streaming) |
| **Enter** | Send chat message |
| **🎤 Mic Button** | Record voice message |
| **Shuffle Gallery** | Load a new random set of 4 images |
| **Hover on Card** | Reveal the Dylan Lens reimagined version |
| **Click on Card** | Open full lightbox comparison view |
| **Esc** | Close lightbox |

---

## 🔧 Service Ports

| Service | Port | Machine | Purpose |
|---------|------|---------|---------|
| Chat API | 8000 | Mac | LangGraph agent + TTS orchestration |
| TTS (XTTS v2) | 8001 | Mac | Dylan voice synthesis |
| Gallery API | 8002 | Mac | Image search + processing + frontend |
| LM Studio | 1234 | GPU PC | Mistral Nemo + LLaVA inference |
| ComfyUI | 8188 | GPU PC | Stable Diffusion img2img |
| Pixel Streaming | 80 | GPU PC | Unreal Engine 3D character |
| UE Bridge | 8500 | GPU PC | Audio relay for lip sync |

---

## 🌐 Network (Tailscale)

| Device | Tailscale IP | Role |
|--------|-------------|------|
| MacBook | 100.66.237.18 | Backend host |
| GPU Desktop | 100.95.111.63 | LM Studio + ComfyUI |
| UE Machine | 100.69.114.80 | Pixel Streaming + Bridge |

---

## 🔗 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Redirects to gallery frontend |
| `/gallery` | GET | Serves the frontend |
| `/health` | GET | Health check (LM Studio + ComfyUI status) |
| `/gallery-stream` | GET | SSE pipeline: search → download → interpret → reimagine |
| `/random-gallery` | GET | Returns random pre-processed images for instant display |
| `/chat` | POST | Send text message, get AI response + audio |
| `/voice-chat` | POST | Send voice recording, get transcription + AI response |

---

## 🎵 Tech Stack

- **Backend:** FastAPI, LangGraph, LangChain
- **LLMs:** Mistral Nemo (chat), LLaVA 1.6 (vision)
- **TTS:** Coqui XTTS v2 (voice cloning)
- **STT:** OpenAI Whisper
- **Image Gen:** ComfyUI + Stable Diffusion (DreamShaper 8)
- **3D:** Unreal Engine 5.6.1, MetaHuman Rig, Pixel Streaming
- **Animation:** NVIDIA Audio2Face 3, AnimBPMH workflow
- **Vector DB:** ChromaDB
- **Frontend:** Vanilla JS, HTML5, CSS3
- **Network:** Tailscale VPN

---

## 📝 Notes

- TTS server requires **Python 3.11** (Coqui TTS doesn't support 3.12+). Use the dedicated `tts_server_venv/`.
- ComfyUI must be started with `--listen 0.0.0.0` for remote access.
- LM Studio needs both **Mistral Nemo** (chat) and **LLaVA** (gallery) models loaded simultaneously.
- The gallery loads 4 random pre-processed images on startup for instant display. Use the **Shuffle Gallery** button to load new random images.
- The full SSE pipeline (search → download → interpret → reimagine) is still available via the `/gallery-stream` endpoint.
- The gallery falls back to [Picsum](https://picsum.photos) test images when no Google API key is configured.

---

## 📄 License

This project is for educational and artistic purposes.

> *"The times they are a-changin'"* — Bob Dylan
