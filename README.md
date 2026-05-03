# 🎸 Bob Dylan AI Portal: Setup Guide

Welcome to the **Bob Dylan AI Portal**. This project is a multi-layered "Digital Twin" and "Poetic Museum" designed to bring the spirit of Bob Dylan to life using distributed AI systems.

This guide is written for anyone—even if you've never used these tools before—to help you set up the entire ecosystem from scratch.

---

## 👁️ What is this Project?

This isn't just a chatbot. It is a **distributed AI experience** consisting of:
1.  **The Digital Twin**: A 3D MetaHuman (Unreal Engine) that talks to you in Dylan's cloned voice, with lips and expressions driven by AI in real-time.
2.  **The Dylan Lens Gallery**: A digital museum that takes modern photos, interprets them through "Dylan's eyes" (Vision AI), and reimagines them as 1960s vintage film photography (Generative AI).

---

## 🏗️ System Architecture (The "Frankenstein" Setup)

Because this project requires heavy AI processing, it usually runs across **multiple machines** connected via a virtual private network (**Tailscale**):

*   **Mac/Linux (The Brain):** Runs the main logic, the Chat API, the Gallery API, and the Voice Cloning server.
*   **Windows GPU PC (The Eyes & Body):** Runs Unreal Engine 5 (3D Graphics), LM Studio (Language Models), and ComfyUI (Image Generation).

---

## 🛠️ Prerequisites

Before you start, make sure you have:
1.  **Hardware:** A PC with a modern NVIDIA GPU (RTX 3060 or better) is highly recommended for the AI models.
2.  **Tailscale:** Install [Tailscale](https://tailscale.com/) on all machines so they can "see" each other securely.
3.  **Python:** 
    *   **Python 3.12** for the main logic.
    *   **Python 3.11** specifically for the Voice Cloning (XTTS) server.
4.  **Package Manager:** Install [uv](https://github.com/astral-sh/uv) (it's a much faster way to handle Python projects).
    *   *Mac command:* `brew install uv`
    *   *Windows/Linux:* See [uv docs](https://github.com/astral-sh/uv).

---

## 🚀 Step-by-Step Installation

### 1. Clone the Repository
Open your terminal and run:
```bash
git clone https://github.com/littleborek/bob-dylan-chatbot.git
cd bob-dylan-chatbot
```

### 2. Set Up Python Environments
This project uses two different Python versions.

**A. Main Environment (Python 3.12):**
```bash
uv venv --python 3.12
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
uv pip install -e .        # Installs all dependencies from pyproject.toml
```

**B. TTS Environment (Python 3.11):**
Coqui XTTS (the voice cloner) *requires* Python 3.11.
```bash
# Create a separate folder for the TTS venv
uv venv tts_server_venv --python 3.11
source tts_server_venv/bin/activate
uv pip install TTS fastapi uvicorn  # Basic requirements for the voice server
```

### 3. Configure Your Environment Variables
You need a `.env` file to tell the Mac where the GPU PC is.
1.  Copy the example: `cp .env.example .env` (or create a file named `.env`).
2.  Open `.env` in a text editor and update the IPs:
    ```env
    # Replace these IPs with your GPU PC's Tailscale IP
    LMSTUDIO_BASE=http://100.95.111.63:1234
    COMFYUI_BASE=http://100.95.111.63:8188
    
    # Optional: For Google Image search in the gallery
    GOOGLE_API_KEY=your_key_here
    GOOGLE_CSE_ID=your_id_here
    ```

---

## 🛰️ Preparing the Remote Services (GPU PC)

On your **Windows/GPU Machine**, you need to have three things running:

1.  **LM Studio:** 
    *   Load **Mistral Nemo Instruct** (for chat).
    *   Load **LLaVA 1.6** (for vision).
    *   Start the "Local Server" on port `1234`.
2.  **ComfyUI:**
    *   Start ComfyUI with the `--listen 0.0.0.0` flag so the Mac can reach it.
    *   Ensure you have the **DreamShaper v8** model in your models folder.
3.  **Unreal Engine 5:**
    *   Open the `Bob-Dylan-artroom` project.
    *   Ensure **Pixel Streaming** is active.
    *   Run `python ue_bridge.py` (this script receives audio from the Mac and sends it to Dylan's lips).

---

## 🏃 Running the Portal

You will need **three terminal windows** open on your Mac:

### Terminal 1: Voice Cloning (XTTS)
```bash
./tts_server_venv/bin/python tts_server.py
```
*Wait until you see "TTS Server running on port 8001".*

### Terminal 2: Main Chat Backend
```bash
uv run uvicorn main:app --host 0.0.0.0 --port 8000
```
*This handles the "Brain" (LangGraph) and RAG system.*

### Terminal 3: Gallery & Frontend
```bash
uv run uvicorn gallery_server:app --host 0.0.0.0 --port 8002
```
*This serves the website you see in your browser.*

---

## 🎮 How to Use

1.  Open your browser to: `http://localhost:8002`
2.  **Interact:**
    *   **Chat:** Type in the box or click the **Mic 🎤** to talk.
    *   **Digital Twin:** Press the **'T'** key on your keyboard to trigger the "Talk to Dylan" mode in the 3D view.
    *   **Gallery:** Click **Shuffle Gallery** to see new AI-reimagined photos.
    *   **Hover:** Hover your mouse over any image in the gallery to see the "Dylan Lens" (the AI-transformed version).

---

## 🆘 Troubleshooting

*   **"Connection Refused":** Make sure Tailscale is connected on BOTH machines and that the IPs in your `.env` match.
*   **No Sound/Lips not moving:** Check Terminal 4 on the Windows machine (`ue_bridge.py`). It must be running to "bridge" the audio to Unreal Engine.
*   **XTTS Errors:** Ensure you are using `tts_server_venv` which must be Python 3.11. XTTS will fail on Python 3.12.
*   **Images not loading:** The gallery requires either a Google Search API key OR it will fall back to random test images. Check your `.env`.

---

## 📜 Credits & License
Created by **Berk Kocabörek** & **Eray Soydal** for CSE 358.
This project is for educational and artistic purposes.

> *"He not busy being born is busy dying."* — Bob Dylan
