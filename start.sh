#!/bin/bash
# ═══════════════════════════════════════════════════
#  Dylan AI — Tüm Servisleri Başlat
#  Kullanım: ./start.sh
# ═══════════════════════════════════════════════════

cd "$(dirname "$0")"

echo "🎸 Dylan AI Portal başlatılıyor..."
echo ""

# Eski süreçleri temizle
echo "🧹 Eski süreçler temizleniyor..."
kill -9 $(lsof -ti:8000) 2>/dev/null
kill -9 $(lsof -ti:8001) 2>/dev/null
kill -9 $(lsof -ti:8002) 2>/dev/null
sleep 1

# 1. TTS Sunucusu (Python 3.11 venv)
echo "🎙️  [Port 8001] TTS Sunucusu başlatılıyor..."
./tts_server_venv/bin/python tts_server.py &
TTS_PID=$!
sleep 2

# 2. Chat Backend
echo "🤖 [Port 8000] Chat Backend başlatılıyor..."
uv run uvicorn main:app --host 0.0.0.0 --port 8000 &
CHAT_PID=$!
sleep 1

# 3. Gallery Backend + Frontend
echo "🎨 [Port 8002] Gallery Backend başlatılıyor..."
uv run uvicorn gallery_server:app --host 0.0.0.0 --port 8002 &
GALLERY_PID=$!
sleep 1

echo ""
echo "═══════════════════════════════════════════════"
echo "  ✅ Dylan AI Portal hazır!"
echo ""
echo "  🌐 Site:     http://localhost:8002"
echo "  🌐 Tailscale: http://100.66.237.18:8002"
echo ""
echo "  Servisler:"
echo "    Chat API  → http://0.0.0.0:8000  (PID: $CHAT_PID)"
echo "    TTS       → http://0.0.0.0:8001  (PID: $TTS_PID)"
echo "    Gallery   → http://0.0.0.0:8002  (PID: $GALLERY_PID)"
echo ""
echo "  Durdurmak için: ./stop.sh veya Ctrl+C"
echo "═══════════════════════════════════════════════"

# Ctrl+C ile hepsini kapat
trap "echo '🛑 Kapatılıyor...'; kill $TTS_PID $CHAT_PID $GALLERY_PID 2>/dev/null; exit" SIGINT SIGTERM

# Logları göster
wait
