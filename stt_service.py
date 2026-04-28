import os
from faster_whisper import WhisperModel

# Model seçimi: 'base' hızlıdır, 'small' veya 'medium' daha kalitelidir.
# 'base' lokalde çoğu cihazda akıcı çalışır.
MODEL_SIZE = "base"

class STTService:
    def __init__(self):
        # CPU üzerinde çalışacak şekilde ayarlıyoruz (Lokal kullanım için en uyumlusu)
        # Eğer NVIDIA GPU varsa device="cuda" yapılabilir.
        print(f"Whisper modeli yükleniyor ({MODEL_SIZE})...")
        self.model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")
        print("Whisper modeli hazır.")

    def transcribe(self, audio_path: str) -> str:
        """
        Verilen ses dosyasını metne çevirir.
        """
        if not os.path.exists(audio_path):
            return "Ses dosyası bulunamadı."

        segments, info = self.model.transcribe(audio_path, beam_size=5)
        
        # Segmentleri birleştirerek tam metni oluştur
        full_text = " ".join([segment.text for segment in segments])
        return full_text.strip()

# Singleton örneği
stt_service = STTService()
