"""
UE Bridge — Dylan AI ses köprüsü
Bu script UE makinesinde çalışır.
Backend WAV gönderince onu belirtilen klasöre kaydeder.
UE bu klasördeki yeni WAV'ı algılayıp lip sync yapar.
"""
import os
import uvicorn
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="UE Audio Bridge")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# WAV dosyalarının kaydedileceği klasör
AUDIO_DIR = os.path.join(os.getcwd(), "C:/Users/Eray/Downloads/Video")
os.makedirs(AUDIO_DIR, exist_ok=True)

@app.post("/speak")
async def receive_audio(
    audio: UploadFile = File(...),
    text: str = Form(default="")
):
    """Backend'den gelen WAV dosyasını kaydet."""
    # Her zaman aynı dosya adına kaydet (UE sürekli bunu okusun)
    output_path = os.path.join(AUDIO_DIR, "as.wav")
    
    with open(output_path, "wb") as f:
        content = await audio.read()
        f.write(content)
    
    # Metni de kaydet (UE subtitle göstermek isterse)
    text_path = os.path.join(AUDIO_DIR, "dylan_speak.txt")
    with open(text_path, "w", encoding="utf-8") as f:
        f.write(text)
    
    print(f"🎙️ New audio received: {len(content)} bytes")
    print(f"   Text: {text[:80]}...")
    print(f"   Saved to: {output_path}")
    
    return {"status": "ok", "message": "Audio saved for UE playback"}

@app.get("/health")
async def health():
    return {"status": "running", "audio_dir": AUDIO_DIR}

if __name__ == "__main__":
    # 0.0.0.0 dinleyerek dışarıdan (Mac'ten) gelen istekleri kabul ederiz
    uvicorn.run(app, host="0.0.0.0", port=8500)
