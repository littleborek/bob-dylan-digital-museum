import os
import shutil
import uuid
import httpx
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from agent import graph
from stt_service import stt_service

app = FastAPI(title="Bob Dylan AI Backend")

# Klasörleri ayarla
TEMP_DIR = "temp_audio"
GENERATED_DIR = "generated_audio"
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(GENERATED_DIR, exist_ok=True)

# Frontend dosyalarını (artroom) ve üretilen sesleri dışarı açıyoruz
app.mount("/artroom", StaticFiles(directory="Bob-Dylan-artroom"), name="artroom")
app.mount("/audio", StaticFiles(directory=GENERATED_DIR), name="audio")

# Frontend'den gelecek istekler için CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

async def generate_dylan_voice(text: str):
    """
    XTTS v2 ses klonlama sunucusunu kullanarak Dylan'ın sesiyle konuşturur.
    """
    try:
        import re
        clean_text = re.sub(r"\[EXPRESSION:.*?\]", "", text).strip()
        if not clean_text:
            return None

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8001/generate",
                json={"text": clean_text, "speaker_wav": "dylan_ref.wav"},
                timeout=120.0  # Ses üretimi CPU'da biraz zaman alıyor
            )
            if response.status_code == 200:
                return response.json().get("audio_url")
    except Exception as e:
        print(f"XTTS Sunucusu hatası: {e}")
    return None

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        config = {"recursion_limit": 10}
        inputs = {"messages": [HumanMessage(content=request.message)]}
        
        final_message = ""
        for event in graph.stream(inputs, config):
            for node, value in event.items():
                if "messages" in value:
                    for msg in value["messages"]:
                        if msg.type == "ai" and not msg.tool_calls:
                            final_message = msg.content
        
        # Sesi üret (Arka planda Dylan konuşsun)
        # Not: Üretim süresi metnin uzunluğuna göre değişir.
        audio_url = await generate_dylan_voice(final_message)
        
        return {
            "response": final_message, 
            "audio_url": audio_url,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/voice-chat")
async def voice_chat_endpoint(file: UploadFile = File(...)):
    file_id = str(uuid.uuid4())
    temp_file_path = os.path.join(TEMP_DIR, f"{file_id}_{file.filename}")
    
    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        transcribed_text = stt_service.transcribe(temp_file_path)
        if not transcribed_text:
            return {"response": "Anlayamadım dostum...", "status": "error"}

        inputs = {"messages": [HumanMessage(content=transcribed_text)]}
        final_message = ""
        for event in graph.stream(inputs, {"recursion_limit": 10}):
            for node, value in event.items():
                if "messages" in value:
                    for msg in value["messages"]:
                        if msg.type == "ai" and not msg.tool_calls:
                            final_message = msg.content

        # Sesi üret
        audio_url = await generate_dylan_voice(final_message)

        return {
            "transcription": transcribed_text,
            "response": final_message,
            "audio_url": audio_url,
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

@app.get("/")
async def root():
    return {"message": "Bob Dylan AI Backend is running. The wind is blowin'..."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
