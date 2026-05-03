"""
Bob Dylan AI Galeri Sunucusu
Akış: Google Görseller → LLaVA (lokal görsel yorum) → Stable Diffusion (yeniden çizim) → Galeri
"""
from dotenv import load_dotenv
load_dotenv()
import os
import base64
import asyncio
import httpx
import uuid
import json
import re
import random as rng
from io import BytesIO
from pathlib import Path
from fastapi import FastAPI, Query
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, RedirectResponse
from pydantic import BaseModel

app = FastAPI(title="Bob Dylan Gallery")

# Galeri görselleri klasörü
GALLERY_DIR = Path("gallery_images")
GALLERY_DIR.mkdir(exist_ok=True)

app.mount("/gallery_images", StaticFiles(directory=str(GALLERY_DIR)), name="gallery_images")
app.mount("/gallery", StaticFiles(directory="gallery-frontend", html=True), name="gallery")
# Frontend: gallery-frontend/index.html (unified), main.css, main.js


@app.get("/")
async def root():
    return RedirectResponse(url="/gallery")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------
# Ayarlar - Kendi API Key'ini .env'e ekle
# -------------------------------------------------------
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GOOGLE_CSE_ID  = os.getenv("GOOGLE_CSE_ID", "")

# LM Studio API Ayarları
LMSTUDIO_BASE  = os.getenv("LMSTUDIO_BASE", "http://localhost:1234")
LMSTUDIO_MODEL = os.getenv("LMSTUDIO_MODEL", "lmstudio-community/llava-v1.6-mistral-7b-gguf")

# ComfyUI API Ayarları
COMFYUI_BASE   = os.getenv("COMFYUI_BASE", "http://localhost:8188")


# -------------------------------------------------------
# Yardımcı Fonksiyonlar
# -------------------------------------------------------

async def fetch_google_images(query: str, count: int = 8) -> list[dict]:
    """Google Custom Search API ile görsel arar."""
    if not GOOGLE_API_KEY or not GOOGLE_CSE_ID:
        # API key yoksa fallback: Picsum test görseli
        return [
            {
                "url": f"https://picsum.photos/seed/{query.replace(' ','')}{i}/800/600",
                "title": f"{query} - {i+1}",
                "source": "picsum"
            }
            for i in range(count)
        ]

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://www.googleapis.com/customsearch/v1",
            params={
                "key": GOOGLE_API_KEY,
                "cx": GOOGLE_CSE_ID,
                "q": query,
                "searchType": "image",
                "num": count,
                "safe": "active",
                "imgType": "photo",
            },
            timeout=15
        )
        data = resp.json()
        items = data.get("items", [])
        return [
            {
                "url": item["link"],
                "title": item.get("title", ""),
                "source": item.get("displayLink", "")
            }
            for item in items
        ]


async def download_image_as_base64(url: str) -> str | None:
    """Görseli indir ve base64'e çevir."""
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            resp = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
            if resp.status_code == 200:
                return base64.b64encode(resp.content).decode()
    except Exception as e:
        print(f"Görsel indirme hatası ({url}): {e}")
    return None


async def interpret_with_lmstudio(image_b64: str) -> str:
    """
    LM Studio OpenAI-uyumlu API ile görseli Bob Dylan tarzında yorumla.
    LM Studio'da görsel anlayan bir model (LLaVA, BakLLaVA vb.) yüklü olmalı.
    """
    prompt = (
        "You are Bob Dylan. Look at this image and write ONE short poetic sentence "
        "(maximum 20 words) about it in your characteristic style — "
        "metaphorical, gritty, and full of imagery. No quotes, just the sentence."
    )
    async with httpx.AsyncClient(timeout=120) as client:
        resp = await client.post(
            f"{LMSTUDIO_BASE}/v1/chat/completions",
            headers={"Content-Type": "application/json"},
            json={
                "model": LMSTUDIO_MODEL,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_b64}"
                                }
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ],
                "max_tokens": 80,
                "temperature": 0.85,
                "stream": False
            }
        )
        result = resp.json()
        text = result.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
        text = re.sub(r'\n+', ' ', text).strip()
        return text[:200]  # max 200 karakter


async def regenerate_with_sd(prompt: str, image_b64: str) -> str | None:
    """
    Kullanıcının gönderdiği ComfyUI JSON akışını kullanarak görseli yeniden oluşturur.
    Akışı img2img (görselden görsele) moduna çevirir.
    """
    try:
        async with httpx.AsyncClient(timeout=300) as client:
            # 1. Görseli ComfyUI'a yükle
            img_data = base64.b64decode(image_b64)
            files = {"image": ("input_image.png", img_data)}
            upload_resp = await client.post(f"{COMFYUI_BASE}/upload/image", files=files)
            if upload_resp.status_code != 200:
                return None
            uploaded_filename = upload_resp.json().get("name")

            # 2. Kullanıcının JSON akışını img2img için modifiye et
            # (Gönderdiğin JSON'ı temel alıyoruz ama EmptyLatent yerine senin görselini yüklüyoruz)
            import random
            workflow = {
                "3": {
                    "inputs": {
                        "seed": random.randint(0, 2**31),
                        "steps": 28, "cfg": 7.5, "sampler_name": "euler",
                        "scheduler": "karras",
                        "denoise": 0.82,  # Orijinalden belirgin şekilde farklılaştır
                        "model": ["4", 0], "positive": ["6", 0], "negative": ["7", 0],
                        "latent_image": ["11", 0]
                    },
                    "class_type": "KSampler"
                },
                "4": {"inputs": {"ckpt_name": "dreamshaper_8.safetensors"}, "class_type": "CheckpointLoaderSimple"},
                "6": {
                    "inputs": {
                        "text": (
                            f"1960s folk music album cover, Bob Dylan era, "
                            f"analog film grain, Kodachrome photography, faded colors, "
                            f"high contrast black and white vignette, cinematic, "
                            f"protest era americana, worn paper texture, "
                            f"{prompt[:100]}"
                        ),
                        "clip": ["4", 1]
                    },
                    "class_type": "CLIPTextEncode"
                },
                "7": {
                    "inputs": {
                        "text": "modern, digital, sharp, clean, colorful, cartoon, watermark, text, 2020s, plastic",
                        "clip": ["4", 1]
                    },
                    "class_type": "CLIPTextEncode"
                },
                "8": {"inputs": {"samples": ["3", 0], "vae": ["4", 2]}, "class_type": "VAEDecode"},
                "9": {"inputs": {"filename_prefix": "DylanGallery", "images": ["8", 0]}, "class_type": "SaveImage"},
                "10": {"inputs": {"image": uploaded_filename}, "class_type": "LoadImage"},
                "11": {"inputs": {"pixels": ["10", 0], "vae": ["4", 2]}, "class_type": "VAEEncode"}
            }

            # 3. Prompt'u gönder
            prompt_resp = await client.post(f"{COMFYUI_BASE}/prompt", json={"prompt": workflow})
            if prompt_resp.status_code != 200:
                return None
            prompt_id = prompt_resp.json().get("prompt_id")

            # 4. İşlemin bitmesini bekle (Polling)
            for _ in range(60): # Max 1 dakika bekle
                await asyncio.sleep(1)
                hist_resp = await client.get(f"{COMFYUI_BASE}/history/{prompt_id}")
                if hist_resp.status_code == 200:
                    history = hist_resp.json().get(prompt_id)
                    if history and "outputs" in history:
                        # Çıktı dosyasını al
                        images = history["outputs"]["9"]["images"]
                        if images:
                            out_file = images[0]["filename"]
                            # Görseli çek
                            view_resp = await client.get(f"{COMFYUI_BASE}/view", params={"filename": out_file})
                            if view_resp.status_code == 200:
                                return base64.b64encode(view_resp.content).decode()
            return None
    except Exception as e:
        print(f"ComfyUI Error: {e}")
        return None


def save_base64_image(b64: str, prefix: str = "img", image_hash: str = None) -> str:
    """base64 görseli dosyaya kaydet, URL döndür."""
    if not image_hash:
        image_hash = uuid.uuid4().hex[:8]
    filename = f"{prefix}_{image_hash}.jpg"
    path = GALLERY_DIR / filename
    image_bytes = base64.b64decode(b64)
    with open(path, "wb") as f:
        f.write(image_bytes)
    return f"/gallery_images/{filename}"


# -------------------------------------------------------
# SSE: Server-Sent Events ile Gerçek Zamanlı Pipeline
# -------------------------------------------------------

async def gallery_pipeline(query: str, count: int):
    """
    Her fotoğraf için pipeline'ı çalıştır ve SSE olarak gönder.
    Format: data: <json>\n\n
    """
    def send(event_type: str, payload: dict) -> str:
        return f"data: {json.dumps({'event': event_type, **payload})}\n\n"

    yield send("start", {"message": f"Searching for '{query}'...", "total": count})

    images = await fetch_google_images(query, count)

    if not images:
        yield send("error", {"message": "No images found on Google."})
        return

    for idx, img_info in enumerate(images):
        yield send("progress", {"message": f"Processing {idx+1}/{len(images)}: {img_info['title'][:40]}", "index": idx})

        # 1) Görseli indir
        original_b64 = await download_image_as_base64(img_info["url"])
        if not original_b64:
            # İndirilemezse atla
            yield send("skip", {"index": idx, "reason": "İndirilemedi"})
            continue

        img_hash = uuid.uuid4().hex[:8]
        # Orijinali kaydet
        original_url = save_base64_image(original_b64, "orig", img_hash)
        yield send("original_ready", {"index": idx, "url": original_url, "title": img_info["title"]})

        # 2) LM Studio (LLaVA) ile yorumla
        try:
            interpretation = await interpret_with_lmstudio(original_b64)
        except Exception as e:
            interpretation = "Sometimes even silence speaks louder than the wind."
            print(f"LLaVA hatası: {e}")

        yield send("interpreted", {"index": idx, "quote": interpretation})

        # 3) Stable Diffusion ile yeniden oluştur
        sd_image_url = None
        try:
            sd_b64 = await regenerate_with_sd(interpretation, original_b64)
            if sd_b64:
                sd_image_url = save_base64_image(sd_b64, "sd", img_hash)
        except Exception as e:
            print(f"SD hatası (atlanıyor): {e}")

        # Kartı gönder
        yield send("card_ready", {
            "index": idx,
            "original_url": original_url,
            "sd_url": sd_image_url,
            "quote": interpretation,
            "title": img_info["title"],
            "source": img_info.get("source", "")
        })

    yield send("done", {"message": "Gallery is ready."})


@app.get("/gallery-stream")
async def gallery_stream(query: str = Query(default="road"), count: int = Query(default=8, ge=1, le=20)):
    """SSE endpoint - Gallery pipeline'ını gerçek zamanlı akıtır."""
    return StreamingResponse(
        gallery_pipeline(query, count),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        }
    )


@app.get("/health")
async def health():
    # LM Studio ve ComfyUI durumunu kontrol et
    status = {"lmstudio": False, "comfyui": False}
    async with httpx.AsyncClient(timeout=3) as client:
        try:
            r = await client.get(f"{LMSTUDIO_BASE}/v1/models")
            status["lmstudio"] = r.status_code == 200
            models = [m["id"] for m in r.json().get("data", [])]
            status["lmstudio_models"] = models
        except Exception:
            pass
        try:
            r = await client.get(f"{COMFYUI_BASE}/system_stats")
            status["comfyui"] = r.status_code == 200
        except Exception:
            pass
    return status


async def process_single_image(orig_path: Path):
    """Mevcut bir görseli LLaVA + SD ile işle."""
    img_hash = orig_path.name.replace("orig_", "").replace(".jpg", "")
    sd_path = GALLERY_DIR / f"sd_{img_hash}.jpg"
    
    if sd_path.exists():
        return # Zaten işlenmiş
    
    print(f"Processing archive image: {img_hash}")
    try:
        with open(orig_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode()
        
        # 1. LLaVA
        interpretation = await interpret_with_lmstudio(img_b64)
        
        # 2. Stable Diffusion
        sd_b64 = await regenerate_with_sd(interpretation, img_b64)
        if sd_b64:
            save_base64_image(sd_b64, "sd", img_hash)
            # Quote'u bir meta dosyasına kaydedebiliriz ama şu an basitleştirelim
            meta_path = GALLERY_DIR / f"meta_{img_hash}.json"
            with open(meta_path, "w") as f:
                json.dump({"quote": interpretation, "processed": True}, f)
            print(f"Successfully reimagined {img_hash}")
    except Exception as e:
        print(f"Error processing archive image {img_hash}: {e}")


@app.get("/process-archive")
async def process_archive(limit: int = 5):
    """Arşivdeki işlenmemiş görselleri arka planda işlemeye başlar."""
    originals = list(GALLERY_DIR.glob("orig_*.jpg"))
    to_process = []
    for orig in originals:
        img_hash = orig.name.replace("orig_", "").replace(".jpg", "")
        if not (GALLERY_DIR / f"sd_{img_hash}.jpg").exists():
            to_process.append(orig)
    
    selected = to_process[:limit]
    
    # Arka planda çalıştır
    async def bg_task():
        for path in selected:
            await process_single_image(path)
            
    asyncio.create_task(bg_task())
    
    return {"message": f"Started processing {len(selected)} images in background.", "remaining_queue": len(to_process) - len(selected)}


@app.get("/random-gallery")
async def random_gallery(count: int = Query(default=4, ge=1, le=12)):
    """
    Return random gallery images. Prioritizes reimagined (SD) images.
    If an image is original-only, triggers background processing.
    """
    originals = list(GALLERY_DIR.glob("orig_*.jpg"))
    sd_hashes = {f.name.replace("sd_", "").replace(".jpg", "") for f in GALLERY_DIR.glob("sd_*.jpg")}
    
    # Processed ones
    processed = [f for f in originals if f.name.replace("orig_", "").replace(".jpg", "") in sd_hashes]
    # Unprocessed ones
    unprocessed = [f for f in originals if f.name.replace("orig_", "").replace(".jpg", "") not in sd_hashes]
    
    # We want a mix but mostly processed if available
    if len(processed) >= count:
        selected = rng.sample(processed, count)
    else:
        selected = processed + rng.sample(unprocessed, min(count - len(processed), len(unprocessed)))

    sd_files = {f.name.replace("sd_", ""): f for f in GALLERY_DIR.glob("sd_*.jpg")}
    results = []

    quotes = [
        "The wind carries stories that no man can hold.",
        "Behind every shadow, there's a song waiting to be born.",
        "The road stretches on like an unfinished verse.",
        "Even the rain has a rhythm if you listen close enough.",
        "Sometimes the silence speaks louder than the storm.",
        "Every stranger's face tells a tale of highways and heartbreak.",
        "The morning light don't ask permission to shine.",
        "There's a melody hiding in the dust of every town.",
        "Time moves like a river with no intention of return.",
        "The truth ain't always pretty, but it sings its own song.",
    ]

    for i, orig in enumerate(selected):
        orig_url = f"/gallery_images/{orig.name}"
        img_hash = orig.name.replace("orig_", "").replace(".jpg", "")
        sd_file = sd_files.get(img_hash + ".jpg")
        sd_url = f"/gallery_images/{sd_file.name}" if sd_file else None
        
        # If not processed, trigger background processing
        if not sd_url:
            asyncio.create_task(process_single_image(orig))
        
        # Quote reading
        quote = rng.choice(quotes)
        meta_path = GALLERY_DIR / f"meta_{img_hash}.json"
        if meta_path.exists():
            try:
                with open(meta_path, "r") as f:
                    meta = json.load(f)
                    quote = meta.get("quote", quote)
            except: pass

        results.append({
            "index": i,
            "original_url": orig_url,
            "sd_url": sd_url,
            "quote": quote,
            "title": f"Dylan Lens #{i + 1}",
            "source": "Gallery Archive"
        })

    return {"images": results}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
