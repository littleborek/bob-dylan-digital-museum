# KNOCK — Design Your Door

## Bob Dylan AI Portal: A Digital Twin, A Poetic Museum

**CSE 358 Introduction to Artificial Intelligence — Creative Project Assignment**
**Spring 2025–2026**

> *"Mama, take this badge off of me / I can't use it anymore"*
> — Bob Dylan, *Knockin' on Heaven's Door* (1973)

---

**Team Members:**

| Name | Student ID |
|------|-----------|
| Berk Kocabörek | 20230808607 |
| Eray Soydal | 20230808605 |

---

## Artist's Manifesto

### 1. Why This Medium?

At first, we considered building a simple chatbot. But the more we listened to Dylan, the more we read about him, the more we realized that Dylan doesn't just speak — he exists. When he steps on stage, he doesn't merely sing; he carries an atmosphere, an era, an attitude. So we decided not to build a system that simply generates text, but to create a **digital twin** — Dylan's spirit inhabiting a digital body — and a **poetic museum** where this twin lives and breathes.

Our project consists of two experiential layers:

**The first layer: the 3D Digital Twin.** A highly detailed MetaHuman character built in Unreal Engine 5.6.1, streamed directly to the browser via Pixel Streaming. This character doesn't just stand there — it converses with the user, responds in Dylan's cloned voice, and its facial expressions and lip movements are driven in real-time by NVIDIA Audio2Face 3 using a custom MetaHuman AnimBPMH (Animation Blueprint) workflow. When the user presses "T" on the keyboard, they enter a direct dialogue with this digital twin.

**The second layer: the Dylan Lens Gallery.** A kind of digital art museum. The photographs presented to the user are first interpreted through Dylan's eyes by LLaVA, then reimagined by Stable Diffusion in the analog film aesthetic of the 1960s. The original and transformed versions are displayed side by side, like panels in a museum exhibition. When you hover over a card, the "Dylan's eye view" of the photograph reveals itself — just like discovering the story behind an artwork in a gallery.

We chose this medium because the "door" metaphor in Dylan's song is a point of interaction. It demands not a passive viewer but an active participant. Looking at a painting is not enough — you need to knock on that door. In our project, knocking means starting a conversation with Dylan, stepping into the gallery, hovering over a photograph and reading the poem beneath it.

There was another reason we merged the digital twin and museum concepts: Dylan has always been an artist who refused to be "put in a museum." When he won the Nobel Prize in Literature in 2016, he didn't even attend the ceremony. We carried this irony into our project — we put him in a museum, but in this museum, he's alive. He talks to visitors, recites poetry, asks questions back. This is a digital response to Dylan's philosophy of refusing to be labeled.

### 2. What Caught Us?

*"Knockin' on Heaven's Door"* was written in 1973 for Sam Peckinpah's film *Pat Garrett & Billy the Kid*. In the film, Sheriff Colin Baker slowly dies after being shot, and this song plays over the scene. Baker's wife watches her husband's blood pool as the lyrics are heard: *"Mama, take this badge off of me / I can't use it anymore."*

This scene struck us deeply. The "badge" here is not just a sheriff's star — it is a symbol of authority, responsibility, every identity that society pins on you. Baker wants to remove his badge as he dies because he no longer needs that identity. This is, in its purest form, a moment of "surrender" and "liberation."

The historical context of 1973 deepens this scene further. The final years of the Vietnam War, the Watergate scandal, the moment when the counterculture movement's idealism gave way to disillusionment. An entire generation was exhausted after fighting for peace and freedom. Dylan himself had already withdrawn from public life after his 1966 motorcycle accident — he had already taken off his own "badge." When he wrote this song in 1973, he was voicing not just a film character's farewell, but an entire generation's goodbye.

We wove this theme of "shedding the badge" into every layer of our project. The RAG knowledge base carries Dylan's anti-authoritarian philosophy, the spirit of the counterculture movement, and the weariness of 1973. The AI agent speaks in metaphors rather than giving advice — exactly as Dylan does in real life. When the gallery takes modern photographs and transforms them into the analog aesthetic of the 1960s, it is essentially "removing today's badges and returning to the authenticity of the past."

### 3. AI as What?

Our relationship with AI in this project cannot be defined by a single word. Throughout the process, AI assumed different roles:

**AI as a medium (spirit-caller):** What was Dylan thinking in 1973? We can never know exactly. But we processed his biographies, interviews, and song lyrics into a vector database (ChromaDB), and fed the Mistral-Nemo model with this data. The result was Dylan's "digital ghost" — not entirely accurate, but close to his spirit. The RAG system here is the modern version of a séance.

**AI as a translator:** When the LLaVA model looks at a photograph, it interprets it not in technical terms but in Dylan's poetic language. Stable Diffusion then takes this interpretation and transforms it into a visual translation — a modern street photo is reborn with the Kodachrome film grain and sepia tones of the 1960s. AI here is a translator between eras.

**AI as an animator and mask:** We utilized a custom MetaHuman rig combined with NVIDIA Audio2Face 3 directly within Unreal Engine. This AI model takes the generated audio stream and translates it into real-time facial muscle movements via the AnimBPMH (Animation Blueprint MetaHuman) workflow. This is AI's most provocative role — a usage that questions the fluidity of identity and the reality behind the digital mask. Dylan says, "I can only be me, whoever that is." With the MetaHuman twin, we asked: "Where does the boundary of who we are end?"

**AI as a voice:** XTTS v2 produced a voice clone from Dylan's audio samples. When the AI-generated text is spoken in Dylan's voice, a strange "uncanny valley" emerges — familiar yet foreign, real yet artificial. This tension is an intentional part of the project. The digital twin is not exactly Dylan — but it's not exactly not-Dylan either.

### 4. Our Door

What does "knocking on heaven's door" mean to us?

We are two computer engineering students. We spend most of our lives among algorithms, data structures, and compiler errors. In this project, for the first time, we were asked to produce a "work of art" — and this was a genuine threshold for us.

Writing code is easy. Calling an API, integrating a model — these are our comfort zone. But answering the question "what does this song say to you?", confronting our own vulnerability, saying "I" in a manifesto — these are an entirely different kind of challenge.

Throughout this project, we realized that no matter how powerful AI becomes, it cannot encode how a song makes you feel. You can clone Dylan's voice, imitate his face, analyze his lyrics — but no model can produce that thing that stirs inside you when you listen to that song. That was our door: the threshold where technical competence ends and human experience begins.

And perhaps Dylan's desire to "take off his badge" is exactly this — to set aside all the labels, expectations, and the "engineer" identity for a moment, and simply be human, alone with a song.

---

## Technical Architecture

### AI Techniques Used and Their Interactions

Our project integrates five distinct AI technique families into an interdependent pipeline:

| # | Technique | Model / Tool | Family | Role |
|---|-----------|-------------|--------|------|
| 1 | LLM + RAG Pipeline | Mistral-Nemo-Instruct-2407 + ChromaDB + LangGraph | NLP / Retrieval | Conversational intelligence with historical context |
| 2 | Vision-Language Model | LLaVA-1.6-Mistral-7b | Multimodal AI | Visual analysis and poetic interpretation |
| 3 | Image-to-Image Diffusion | DreamShaper v8 (ComfyUI) | Generative Vision | Vintage style transformation |
| 4 | Voice Cloning (TTS) | Coqui XTTS v2 | Speech Synthesis | Dylan voice clone |
| 5 | Real-time Facial Animation | NVIDIA Audio2Face 3 | Audio-to-Animation | Drives MetaHuman facial rig from audio |
| 6 | 3D Character Rigging | MetaHuman + AnimBPMH | Real-time 3D | High-fidelity digital twin body and face |
| 7 | Speech-to-Text | Faster Whisper (base) | ASR | Voice chat input |

**How the techniques interact:** These techniques are not isolated. When a user sends a voice message, Whisper (STT) converts it to text → Mistral-Nemo pulls historical context from RAG and generates a Dylan-style response → XTTS v2 voices this response in Dylan's cloned voice → the WAV file is sent to the Unreal Engine machine → NVIDIA Audio2Face 3 processes the audio to drive the MetaHuman rig via the AnimBPMH workflow, resulting in realistic lip synchronization and facial expressions. A single user interaction triggers multiple AI techniques in sequence.

### Distributed System Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    BROWSER (Frontend)                        │
│  ┌─────────────────┐  ┌───────────────────────────────────┐  │
│  │ Pixel Streaming  │  │         Chat Panel                │  │
│  │ (iframe → UE5)   │  │  Text + Voice → AI reply + audio  │  │
│  │ Press T to talk  │  │                                   │  │
│  └─────────────────┘  └───────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────┐│
│  │              Dylan Lens Gallery (Museum)                   ││
│  │  Random pre-loaded images • Shuffle to explore            ││
│  │  LLaVA interpretation → ComfyUI vintage reimagining       ││
│  └───────────────────────────────────────────────────────────┘│
└──────────────┬───────────────────────────┬───────────────────┘
               │                           │
        ┌──────▼──────┐            ┌───────▼───────┐
        │  main.py    │            │gallery_server │
        │  Port 8000  │            │  Port 8002    │
        │  Chat API   │            │  Gallery API  │
        └──────┬──────┘            └───────┬───────┘
               │                           │
    ┌──────────▼──────────┐     ┌──────────▼──────────┐
    │   LangGraph Agent   │     │   LLaVA (Vision)    │
    │   + RAG (ChromaDB)  │     │   + ComfyUI (SD)    │
    │   + Wikipedia       │     │   DreamShaper v8    │
    │   (Mistral Nemo)    │     │                     │
    └──────────┬──────────┘     └─────────────────────┘
               │
    ┌──────────▼──────────┐     ┌─────────────────────┐
    │   XTTS v2 (TTS)    │────▶│  UE Bridge (8500)   │
    │   Port 8001         │     │  → Lip Sync WAV     │
    │   Dylan Voice Clone │     │  → Audio2Face 3     │
    └─────────────────────┘     │  → MetaHuman Rig    │
                                └─────────────────────┘
```

**Node A — Berk's PC:** FastAPI backend (main.py, gallery_server.py), LM Studio (Mistral-Nemo-Instruct-2407 + LLaVA-1.6-Mistral-7b models), ComfyUI (Stable Diffusion + DreamShaper v8), XTTS v2 voice cloning server, ChromaDB vector database, Faster Whisper STT, web frontend.

**Node B — Eray's PC (Windows):** Unreal Engine 5.6.1 (Pixel Streaming), NVIDIA Audio2Face 3, MetaHuman Rig, UE Audio Bridge.

Both machines are connected via Tailscale VPN, operating as a single local network.

### Codebase Structure

```
bob-dylan/
├── main.py                 # Main chat backend (FastAPI, port 8000)
├── agent.py                # LangGraph agent (Mistral Nemo + tools)
├── rag.py                  # RAG / ChromaDB vector store setup
├── stt_service.py          # Faster Whisper speech-to-text
├── tts_server.py           # XTTS v2 voice cloning server (port 8001)
├── gallery_server.py       # Gallery backend (FastAPI, port 8002)
├── ue_bridge.py            # UE audio bridge (port 8500)
├── dylan_ref.wav           # Dylan voice reference for cloning
├── gallery-frontend/       # Web interface
│   ├── index.html          # Unified SPA interface
│   ├── main.css            # Vintage + modern design system
│   └── main.js             # Chat, gallery, lightbox logic
├── data/                   # Dylan knowledge base (RAG source)
│   ├── dylan_biography.txt # Biography and historical context
│   └── dylan_data.txt      # Philosophy, song meanings, personality
├── chroma_db/              # Vector database (persistent)
├── Bob-Dylan-artroom/      # 3D scene assets
└── generated_audio/        # Generated audio files
```

### How Historical Context Is Embedded in the System (Constraint 3)

Historical context in our project is not a superficial reference but a structural element woven into the system's DNA:

1. **RAG Knowledge Base:** The documents in the `data/` directory contain Dylan's philosophy from the 1960s–70s, song meanings, and personality traits. These are vectorized into ChromaDB using the `all-MiniLM-L6-v2` embedding model. When a user asks a philosophical question, the LangGraph agent retrieves relevant context from this database.

2. **System Prompt Design:** The AI agent is configured with a system prompt: *"You are Bob Dylan. Your speaking style is poetic, philosophical, and sometimes mysterious."* Rules for metaphorical speech, answering questions with questions, and avoiding didactic tone are explicitly defined.

3. **Visual Aesthetic:** The ComfyUI workflow prompts directly reference the 1960s–70s era: *"1960s folk music album cover, Bob Dylan era, analog film grain, Kodachrome photography, faded colors, protest era americana, worn paper texture."* Negative prompts exclude modern aesthetics: *"modern, digital, sharp, clean, colorful, cartoon, 2020s."*

4. **Pat Garrett & Billy the Kid Connection:** The XTTS v2 voice reference carries the acoustic character of the 1973 era. The digital twin's voice reflects the timbre of the period when the song was written.

---

## AI Tools and Technologies Used

| Tool / Model | Version | Purpose |
|-------------|---------|---------|
| Mistral-Nemo-Instruct-2407 | GGUF (LM Studio) | Primary chat LLM |
| LLaVA-1.6-Mistral-7b | GGUF (LM Studio) | Visual analysis and interpretation |
| DreamShaper v8 | safetensors (ComfyUI) | Stable Diffusion img2img |
| Coqui XTTS v2 | multilingual/multi-dataset | Voice cloning |
| Faster Whisper | base (int8) | Speech recognition |
| NVIDIA Audio2Face 3 | Unreal Engine Plugin | Real-time facial animation from audio |
| MetaHuman | Epic Games | High-fidelity 3D character rig |
| HuggingFace all-MiniLM-L6-v2 | sentence-transformers | Text embedding (RAG) |
| LangGraph + LangChain | Python | Agent orchestration |
| ChromaDB | Local | Vector database |
| Unreal Engine 5.6.1 | Pixel Streaming | 3D character and scene |
| FastAPI | Python | Backend API server |

---

## Challenges and Solutions

Building this digital twin portal was far from a linear path. We encountered several technical thresholds that forced us to rethink our approach:

1. **The Rigging Bottleneck:** Initially, we sourced high-quality 3D models specifically designed to look exactly like Bob Dylan. However, we quickly realized that these models were "dead" — they had no facial rig. Without a complex blendshape system or bone structure for the face, we couldn't make them speak. This led us to our most significant pivot: using **Epic Games' MetaHuman** framework. While it required us to meticulously recreate Dylan's features within the MetaHuman Creator, it provided the high-fidelity rigging necessary for real-time AI-driven animation.

2. **Facial Performance at Scale:** Even with a rigged character, making it respond to audio in real-time was a hurdle. We moved away from traditional lip-sync techniques to **NVIDIA Audio2Face 3**. Integrating this into the MetaHuman AnimBPMH workflow required balancing visual realism with the performance constraints of a distributed network.

3. **Orchestrating a Distributed System:** Our project is a "frankenstein" of different operating systems and hardware. The logic runs on macOS, the 3D world on Windows, and the AI models on a remote GPU. Connecting these via **Tailscale VPN** and ensuring that a voice request from the browser travels through five different AI models and two machines to result in a lip-synced response in Unreal Engine was a massive networking and latency challenge.

---

## Team Contributions

**Eray Soydal (20230808605):**
- Unreal Engine 5.6.1 scene design and Pixel Streaming setup
- MetaHuman rig setup and AnimBPMH workflow integration
- NVIDIA Audio2Face 3 integration for real-time facial animation
- UE Audio Bridge (ue_bridge.py) for audio streaming
- 3D environment visual aesthetics and atmosphere design
- Live exhibition performance setup

**Berk Kocabörek (20230808607):**
- FastAPI backend architecture (main.py, gallery_server.py)
- LangGraph agent programming (agent.py)
- LM Studio model management (Mistral-Nemo + LLaVA)
- ComfyUI workflow design (Stable Diffusion + DreamShaper)
- RAG system: data collection, ChromaDB integration (rag.py)
- XTTS v2 voice cloning server and speaker embedding optimization (tts_server.py)
- Web interface: HTML/CSS/JS frontend design and SSE pipeline
- Whisper STT integration (stt_service.py)
- System orchestration and Tailscale network configuration

---

## Conclusion

Dylan once said, *"An artist's job isn't to tell people what to think, but to create a space for them to think."* That is exactly what we tried to do — we created a space for thinking. A space where you can converse with a digital twin, lose yourself in an art gallery, and walk the dusty roads of 1973.

We designed the door. Now it's time to knock.

> *"The door is yours to design. What's behind it is yours to discover."*

---










https://github.com/user-attachments/assets/1e5c54fc-949e-4c39-bee1-45dec3b4bef2

<img width="1280" height="832" alt="resim" src="https://github.com/user-attachments/assets/95f867fd-3731-4ba4-8bb9-d159ed6f1e60" />


<img width="871" height="891" alt="resim" src="https://github.com/user-attachments/assets/908acf2c-884c-40c6-8469-22266d706fd8" />

<img width="1128" height="703" alt="resim" src="https://github.com/user-attachments/assets/b67e4e57-f673-4541-9502-b3d261e9a118" />

https://github.com/user-attachments/assets/b69de2c5-0303-4dd5-b3d7-c1dfd2bacea8



**References:**
- Dylan, B. (1973). *Knockin' on Heaven's Door* [Song]. Columbia Records.
- Peckinpah, S. (Director). (1973). *Pat Garrett & Billy the Kid* [Film]. MGM.
- Jahn, T. (Director). (1997). *Knocking on Heaven's Door* [Film]. Buena Vista.
- Dylan, B. (2016). *Nobel Lecture*. The Nobel Foundation.
- Sounes, H. (2011). *Down the Highway: The Life of Bob Dylan*. Grove Press.
- Marcus, G. (2005). *Like a Rolling Stone: Bob Dylan at the Crossroads*. PublicAffairs.
- Mangold, J. (Director). (2026). *A Complete Unknown* [Film]. Searchlight Pictures.
