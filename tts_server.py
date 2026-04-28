import os
import torch
import uuid
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# PyTorch 2.6+ uyumluluk yaması
original_load = torch.load
torch.load = lambda *args, **kwargs: original_load(*args, **{**kwargs, "weights_only": False})

app = FastAPI()

# XTTS CPU modunda çalışıyor (Apple Silicon MPS kompleks sayı desteklemediği için)
device = "cpu"
print(f"TTS Cihazı: {device}")

print("XTTS v2 modeli yükleniyor...")
from TTS.api import TTS
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
print("XTTS v2 modeli hazır.")

OUTPUT_DIR = "generated_audio"
SPEAKER_WAV = "dylan_ref.wav"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ─── Startup'ta Speaker Embedding'i Hesapla ve Cache'le ───────────────────────
# Bunu her istekte değil, sadece bir kez yapıyoruz → büyük hız kazanımı
gpt_cond_latent = None
speaker_embedding = None

def load_speaker_cache():
    global gpt_cond_latent, speaker_embedding
    if not os.path.exists(SPEAKER_WAV):
        print(f"⚠️  Referans ses bulunamadı: {SPEAKER_WAV}")
        return
    print("Dylan'ın ses karakteri analiz ediliyor (ilk kez, bir kez yapılır)...")
    # XTTS'in iç modelini doğrudan kullanarak embedding hesapla
    gpt_cond_latent, speaker_embedding = tts.synthesizer.tts_model.get_conditioning_latents(
        audio_path=[SPEAKER_WAV],
        gpt_cond_len=30,          # Referanstan 30 sn al
        max_ref_length=60,        # Maksimum 60 sn referans
    )
    print("✅ Ses karakteri cache'lendi! Sonraki istekler çok daha hızlı olacak.")

load_speaker_cache()
# ──────────────────────────────────────────────────────────────────────────────

def detect_language(text: str) -> str:
    """Metnin dilini tespit et."""
    turkish_chars = set('çğışöüÇĞİŞÖÜ')
    if any(c in turkish_chars for c in text):
        return "tr"
    turkish_words = {'bir', 've', 'bu', 'da', 'de', 'mi', 'ne', 'için', 'gibi', 'ben', 'sen', 'nasıl', 'var', 'ne', 'değil'}
    words = set(text.lower().split())
    if len(words & turkish_words) >= 2:
        return "tr"
    return "en"

class TTSRequest(BaseModel):
    text: str
    speaker_wav: str = SPEAKER_WAV
    language: str = ""

@app.post("/generate")
async def generate_voice(request: TTSRequest):
    global gpt_cond_latent, speaker_embedding

    if gpt_cond_latent is None or speaker_embedding is None:
        raise HTTPException(status_code=503, detail="Speaker embedding henüz yüklenmedi.")

    try:
        lang = request.language if request.language else detect_language(request.text)
        print(f"🎙️ Dil: {lang} | '{request.text[:60]}...'")

        output_filename = f"{uuid.uuid4()}.wav"
        output_path = os.path.join(OUTPUT_DIR, output_filename)

        # Cache'lenmiş embedding ile doğrudan ses üret (referansı tekrar analiz etmiyor!)
        import torch
        with torch.no_grad():
            out = tts.synthesizer.tts_model.inference(
                text=request.text,
                language=lang,
                gpt_cond_latent=gpt_cond_latent,
                speaker_embedding=speaker_embedding,
                temperature=0.7,
                length_penalty=1.0,
                repetition_penalty=10.0,
                top_k=50,
                top_p=0.85,
            )

        # Ses dosyasına yaz
        import soundfile as sf
        import numpy as np
        audio = out["wav"]
        if isinstance(audio, torch.Tensor):
            audio = audio.cpu().numpy()
        sf.write(output_path, audio, 24000)

        return {"audio_url": f"/audio/{output_filename}", "status": "success"}

    except Exception as e:
        print(f"❌ TTS Hatası: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
