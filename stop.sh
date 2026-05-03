#!/bin/bash
# Dylan AI — Tüm Servisleri Durdur
echo "🛑 Dylan AI durduruluyor..."
kill -9 $(lsof -ti:8000) 2>/dev/null && echo "  ✓ Chat (8000) kapatıldı"
kill -9 $(lsof -ti:8001) 2>/dev/null && echo "  ✓ TTS  (8001) kapatıldı"
kill -9 $(lsof -ti:8002) 2>/dev/null && echo "  ✓ Gallery (8002) kapatıldı"
echo "✅ Tüm servisler durduruldu."
