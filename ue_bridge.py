"""
UE Bridge — Dylan AI Ses Köprüsü (Sıfır Bağımlılık)
Sadece Python standart kütüphaneleri kullanır.
UE makinesinde (100.69.114.80) çalıştır:
    python3 ue_bridge.py
"""
import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import cgi

AUDIO_DIR = os.path.expanduser("~/dylan_audio")
os.makedirs(AUDIO_DIR, exist_ok=True)

class BridgeHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/speak":
            content_type = self.headers.get("Content-Type", "")
            
            if "multipart/form-data" in content_type:
                form = cgi.FieldStorage(
                    fp=self.rfile,
                    headers=self.headers,
                    environ={"REQUEST_METHOD": "POST", "CONTENT_TYPE": content_type}
                )
                
                # WAV dosyasını kaydet
                audio_field = form["audio"]
                audio_data = audio_field.file.read()
                wav_path = os.path.join(AUDIO_DIR, "dylan_speak.wav")
                with open(wav_path, "wb") as f:
                    f.write(audio_data)
                
                # Metni kaydet
                text = form.getvalue("text", "")
                txt_path = os.path.join(AUDIO_DIR, "dylan_speak.txt")
                with open(txt_path, "w") as f:
                    f.write(text)
                
                print(f"🎙️  Audio received: {len(audio_data)} bytes")
                print(f"    Text: {text[:80]}")
                print(f"    Saved: {wav_path}")
                
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "ok"}).encode())
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Bad request")
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "running"}).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.end_headers()

if __name__ == "__main__":
    port = 8500
    server = HTTPServer(("0.0.0.0", port), BridgeHandler)
    print(f"🌉 UE Bridge running on 0.0.0.0:{port}")
    print(f"📁 Audio will be saved to: {AUDIO_DIR}")
    print(f"   Waiting for Dylan's voice...")
    server.serve_forever()
