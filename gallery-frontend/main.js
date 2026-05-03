/**
 * Dylan AI — Unified Frontend JS
 * Chat + Gallery (Pre-loaded + ComfyUI Pipeline) + Pixel Streaming (iframe)
 *
 * First load:  Instant pre-processed images from /random-gallery (no GPU)
 * Shuffle:     Full SSE pipeline through ComfyUI (generates new images)
 */

const GALLERY_API = 'http://100.66.237.18:8002';
const CHAT_API    = 'http://100.66.237.18:8000';

// ── Random topics for shuffle (SSE pipeline) ──────
const RANDOM_TOPICS = [
    'highway road trip', 'rainy street', 'protest march', 'folk guitar',
    'train station', 'dusty desert', 'vintage car', 'old bookstore',
    'midnight city', 'lonely bridge', 'autumn leaves', 'harbor boats',
    'mountain cabin', 'jazz club', 'vinyl records', 'typewriter desk',
    'abandoned factory', 'sunset field', 'coffee shop', 'street musician',
    'winter fog', 'open road', 'lighthouse storm', 'campfire night',
    'blues bar', 'freight train', 'prairie wind', 'river crossing'
];

// ── DOM Elements ──────────────────────────────────
const galleryGrid   = document.getElementById('gallery-grid');
const emptyState    = document.getElementById('empty-state');
const shuffleBtn    = document.getElementById('shuffle-btn');
const progressZone  = document.getElementById('progress-zone');
const progressFill  = document.getElementById('progress-fill');
const progressLabel = document.getElementById('progress-label');
const lightbox      = document.getElementById('lightbox');
const lbOriginal    = document.getElementById('lb-original');
const lbDylan       = document.getElementById('lb-dylan');
const lbQuote       = document.getElementById('lb-quote');
const lbClose       = document.getElementById('lb-close');
const lbBackdrop    = document.getElementById('lb-backdrop');
const dotLmstudio   = document.getElementById('dot-lmstudio');
const dotComfyui    = document.getElementById('dot-comfyui');

const userInput     = document.getElementById('user-input');
const sendBtn       = document.getElementById('send-btn');
const micBtn        = document.getElementById('mic-btn');
const messages      = document.getElementById('messages');
const chatStatus    = document.getElementById('chat-status');
const expressionTag = document.getElementById('expression-tag');

// ── State ─────────────────────────────────────────
let activeSSE = null;
let total = 0;
let isRecording = false, mediaRecorder = null, audioChunks = [];

// ── Init ──────────────────────────────────────────
checkHealth();
loadPreProcessedGallery();  // Instant — no GPU needed

// ══════════════════════════════════════════════════
//  HEALTH CHECK
// ══════════════════════════════════════════════════
async function checkHealth() {
    try {
        const r = await fetch(`${GALLERY_API}/health`, { signal: AbortSignal.timeout(4000) });
        const d = await r.json();
        dotLmstudio.className = 'hdot ' + (d.lmstudio ? 'ok' : 'fail');
        dotComfyui.className  = 'hdot ' + (d.comfyui  ? 'ok' : 'fail');
    } catch {
        dotLmstudio.className = dotComfyui.className = 'hdot fail';
    }
}

// ══════════════════════════════════════════════════
//  GALLERY — Mode 1: Pre-processed (first load)
// ══════════════════════════════════════════════════
async function loadPreProcessedGallery() {
    try {
        const r = await fetch(`${GALLERY_API}/random-gallery?count=4`, { signal: AbortSignal.timeout(8000) });
        const d = await r.json();
        const images = d.images || [];

        if (images.length === 0) {
            emptyState.style.display = 'block';
            return;
        }

        emptyState.style.display = 'none';
        galleryGrid.innerHTML = '';

        images.forEach((data, idx) => {
            const card = document.createElement('div');
            card.className = 'card dual-card';
            card.id = `archive-${idx}`;
            card.style.animationDelay = `${idx * 0.12}s`;

            const originalSrc = `${GALLERY_API}${data.original_url}`;
            const dylanSrc = data.sd_url
                ? `${GALLERY_API}${data.sd_url}`
                : originalSrc;
            
            const isProcessing = !data.sd_url;

            card.innerHTML = `
                <div class="card-dual-images">
                    <div class="card-side">
                        <span class="card-label">Original</span>
                        <img class="card-img-single" src="${originalSrc}" alt="${data.title || ''}" loading="lazy">
                    </div>
                    <div class="card-side dylan-side">
                        <span class="card-label label-dylan">Dylan Lens</span>
                        <div class="dylan-img-wrap">
                            <img class="card-img-single dylan-result" src="${dylanSrc}" alt="Dylan version" loading="lazy">
                            <div class="sd-loading-overlay ${isProcessing ? 'active' : ''}">
                                <div class="spinner"></div>
                                <p>Interpreting...</p>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="card-body">
                    <p class="card-quote">"${data.quote}"</p>
                    <div class="card-meta">
                        <span class="badge">${data.sd_url ? 'Reimagined' : 'In Queue'}</span>
                        <span>${data.source || ''}</span>
                    </div>
                </div>
            `;

            card.addEventListener('click', () => openLightbox(data));
            galleryGrid.appendChild(card);
        });
    } catch (e) {
        console.error('Gallery pre-load error:', e);
        emptyState.style.display = 'block';
    }
}

// ══════════════════════════════════════════════════
//  GALLERY — Mode 2: SSE Pipeline (shuffle → ComfyUI)
// ══════════════════════════════════════════════════
shuffleBtn.addEventListener('click', () => {
    startSSEPipeline();
});

function getRandomTopic() {
    return RANDOM_TOPICS[Math.floor(Math.random() * RANDOM_TOPICS.length)];
}

function startSSEPipeline() {
    const topic = getRandomTopic();

    // Close previous SSE
    if (activeSSE) activeSSE.close();

    // UI reset
    galleryGrid.innerHTML = '';
    emptyState.style.display = 'none';
    progressZone.style.display = 'flex';
    progressFill.style.width = '0%';
    progressLabel.textContent = `Exploring "${topic}"...`;
    shuffleBtn.disabled = true;
    shuffleBtn.innerHTML = '<span class="btn-spinner">⟳</span> Generating...';
    total = 4;

    const url = `${GALLERY_API}/gallery-stream?query=${encodeURIComponent(topic)}&count=4`;
    activeSSE = new EventSource(url);

    activeSSE.onmessage = e => {
        try {
            const msg = JSON.parse(e.data);
            handleSSE(msg);
        } catch (err) {
            console.error('SSE parse error:', err);
        }
    };

    activeSSE.onerror = () => {
        finishPipeline();
    };
}

function handleSSE(msg) {
    switch (msg.event) {
        case 'start':
            total = msg.total || 4;
            progressLabel.textContent = msg.message;
            break;

        case 'progress': {
            const pct = ((msg.index + 1) / total) * 50;
            progressFill.style.width = pct + '%';
            progressLabel.textContent = msg.message;
            break;
        }

        case 'original_ready':
            createDualCard(msg.index, msg.url, msg.title);
            break;

        case 'interpreted':
            updateCardQuote(msg.index, msg.quote);
            break;

        case 'card_ready':
            finalizeCard(msg);
            break;

        case 'skip':
            console.warn(`Image ${msg.index} skipped: ${msg.reason}`);
            break;

        case 'error':
            progressLabel.textContent = msg.message;
            break;

        case 'done':
            finishPipeline();
            break;
    }
}

// ── Card creation for SSE pipeline — shows BOTH original & Dylan ──
function createDualCard(index, url, title) {
    const card = document.createElement('div');
    card.className = 'card dual-card';
    card.id = `card-${index}`;
    card.style.animationDelay = `${index * 0.12}s`;
    card.innerHTML = `
        <div class="card-dual-images">
            <div class="card-side">
                <span class="card-label">Original</span>
                <img class="card-img-single" src="${GALLERY_API}${url}" alt="${title || ''}" loading="lazy">
            </div>
            <div class="card-side dylan-side">
                <span class="card-label label-dylan">Dylan Lens</span>
                <div class="dylan-img-wrap">
                    <img class="card-img-single dylan-result" src="" alt="Dylan version" loading="lazy">
                    <div class="sd-loading-overlay active" id="sd-load-${index}">
                        <div class="spinner"></div>
                        <p>Reimagining...</p>
                    </div>
                </div>
            </div>
        </div>
        <div class="card-body">
            <p class="card-quote skeleton-line"></p>
            <div class="card-meta"><span class="badge">Processing</span></div>
        </div>
    `;
    galleryGrid.appendChild(card);
}

function updateCardQuote(index, quote) {
    const card = document.getElementById(`card-${index}`);
    if (!card) return;
    const quoteEl = card.querySelector('.card-quote');
    if (quoteEl) {
        quoteEl.textContent = `"${quote}"`;
        quoteEl.classList.remove('skeleton-line');
    }
}

function finalizeCard(data) {
    const card = document.getElementById(`card-${data.index}`);
    if (!card) return;

    const dylanImg = card.querySelector('.dylan-result');
    const sdLoad = document.getElementById(`sd-load-${data.index}`);

    if (dylanImg) {
        if (data.sd_url) {
            dylanImg.src = `${GALLERY_API}${data.sd_url}`;
            dylanImg.onload = () => {
                if (sdLoad) sdLoad.classList.remove('active');
            };
        } else {
            const origImg = card.querySelector('.card-img-single');
            if (origImg) dylanImg.src = origImg.src;
            dylanImg.style.filter = 'sepia(0.55) contrast(1.18) brightness(0.82) saturate(0.6) hue-rotate(-8deg)';
            if (sdLoad) sdLoad.classList.remove('active');
        }
    }

    if (data.quote) {
        const quoteEl = card.querySelector('.card-quote');
        if (quoteEl) {
            quoteEl.textContent = `"${data.quote}"`;
            quoteEl.classList.remove('skeleton-line');
        }
    }

    const badge = card.querySelector('.badge');
    if (badge) badge.textContent = data.sd_url ? 'Reimagined' : 'Filtered';

    const pct = 50 + (((data.index + 1) / total) * 50);
    progressFill.style.width = pct + '%';

    card.addEventListener('click', () => openLightbox(data));
}

function finishPipeline() {
    if (activeSSE) activeSSE.close();
    activeSSE = null;
    shuffleBtn.disabled = false;
    shuffleBtn.innerHTML = `
        <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="16 3 21 3 21 8"></polyline>
            <line x1="4" y1="20" x2="21" y2="3"></line>
            <polyline points="21 16 21 21 16 21"></polyline>
            <line x1="15" y1="15" x2="21" y2="21"></line>
            <line x1="4" y1="4" x2="9" y2="9"></line>
        </svg>
        Shuffle Gallery
    `;
    progressFill.style.width = '100%';
    progressLabel.textContent = 'Gallery is ready.';
    setTimeout(() => { progressZone.style.display = 'none'; }, 1500);

    if (galleryGrid.children.length === 0) {
        emptyState.style.display = 'block';
    }
}

// ══════════════════════════════════════════════════
//  LIGHTBOX
// ══════════════════════════════════════════════════
function openLightbox(data) {
    lbOriginal.src = `${GALLERY_API}${data.original_url}`;
    lbDylan.src = data.sd_url ? `${GALLERY_API}${data.sd_url}` : `${GALLERY_API}${data.original_url}`;
    lbQuote.textContent = data.quote || '';
    lightbox.classList.add('open');
}

lbClose.addEventListener('click', () => lightbox.classList.remove('open'));
lbBackdrop.addEventListener('click', () => lightbox.classList.remove('open'));
document.addEventListener('keydown', e => { if (e.key === 'Escape') lightbox.classList.remove('open'); });

// ══════════════════════════════════════════════════
//  CHAT — Text & Voice
// ══════════════════════════════════════════════════
sendBtn.addEventListener('click', handleTextChat);
userInput.addEventListener('keypress', e => { if (e.key === 'Enter') handleTextChat(); });

async function handleTextChat() {
    const text = userInput.value.trim();
    if (!text) return;

    addMsg(text, 'user');
    userInput.value = '';
    sendBtn.disabled = true;
    sendBtn.textContent = '...';

    try {
        const r = await fetch(`${CHAT_API}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text })
        });
        const d = await r.json();

        if (d.status === 'success' && d.response) {
            addMsg(d.response, 'ai');

            const exMatch = d.response.match(/\[EXPRESSION:(.*?)\]/);
            if (exMatch && expressionTag) {
                expressionTag.textContent = exMatch[1].trim();
            }

            if (d.audio_url) {
                sendToUnreal({
                    type: 'dylan_speak',
                    text: d.response.replace(/\[EXPRESSION:.*?\]/g, '').trim(),
                    audio_url: `${CHAT_API}${d.audio_url}`,
                    expression: exMatch ? exMatch[1].trim() : 'NEUTRAL'
                });
            }
        } else {
            addMsg(d.detail || 'Something went wrong...', 'ai');
        }
    } catch (e) {
        console.error('Chat error:', e);
        addMsg('Connection error. Is the backend running?', 'ai');
    }

    sendBtn.disabled = false;
    sendBtn.textContent = 'Ask';
}

function addMsg(text, sender) {
    const div = document.createElement('div');
    div.className = `message ${sender}`;
    div.textContent = text.replace(/\[EXPRESSION:.*?\]/g, '').trim();
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
}

function playAudio(url) {
    const audio = new Audio(url);
    audio.play().catch(e => console.log('Audio autoplay blocked:', e));
}

// ── Unreal Engine Communication ───────────────────
function sendToUnreal(data) {
    const psIframe = document.getElementById('ps-iframe');
    if (psIframe && psIframe.contentWindow) {
        psIframe.contentWindow.postMessage(JSON.stringify(data), '*');
        console.log('→ Sent to UE:', data.type, data.expression);
    }
}

// ── Voice Recording (Mic) ─────────────────────────
micBtn.addEventListener('click', toggleRecording);

async function toggleRecording() {
    if (isRecording) {
        mediaRecorder.stop();
        micBtn.classList.remove('recording');
        isRecording = false;
        return;
    }

    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];

        mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
        mediaRecorder.onstop = async () => {
            stream.getTracks().forEach(t => t.stop());
            const blob = new Blob(audioChunks, { type: 'audio/webm' });
            const formData = new FormData();
            formData.append('file', blob, 'recording.webm');

            addMsg('🎤 (voice message)', 'user');

            try {
                const r = await fetch(`${CHAT_API}/voice-chat`, { method: 'POST', body: formData });
                const d = await r.json();
                if (d.transcription) addMsg(`(You said: "${d.transcription}")`, 'system');
                if (d.response) addMsg(d.response, 'ai');
                if (d.audio_url) playAudio(`${CHAT_API}${d.audio_url}`);
            } catch (e) {
                addMsg('Voice processing failed.', 'ai');
            }
        };

        mediaRecorder.start();
        micBtn.classList.add('recording');
        isRecording = true;
    } catch (e) {
        console.error('Mic error:', e);
    }
}

// ── Nav Active Link ───────────────────────────────
document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', () => {
        document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
        link.classList.add('active');
    });
});
