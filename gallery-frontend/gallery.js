/**
 * Bob Dylan AI Gallery — Frontend Logic
 * SSE bağlantısıyla pipeline sonuçlarını gerçek zamanlı gösterir.
 */

const API_BASE = 'http://localhost:8002';

// ─── Element Referansları ─────────────────────────

const queryInput    = document.getElementById('query-input');
const countSelect   = document.getElementById('count-select');
const searchBtn     = document.getElementById('search-btn');
const galleryGrid   = document.getElementById('gallery-grid');
const emptyState    = document.getElementById('empty-state');
const progressZone  = document.getElementById('progress-zone');
const progressFill  = document.getElementById('progress-fill');
const progressLabel = document.getElementById('progress-label');
const lightbox      = document.getElementById('lightbox');
const lbOriginal    = document.getElementById('lb-original');
const lbSd          = document.getElementById('lb-sd');
const lbQuote       = document.getElementById('lb-quote');
const lightboxClose = document.getElementById('lightbox-close');
const lbBackdrop    = document.getElementById('lightbox-backdrop');

// Health dots
const dotLmstudio = document.getElementById('dot-lmstudio');
const dotComfyui  = document.getElementById('dot-comfyui');

// ─── Durum ───────────────────────────────────────

let cards = {}; // index → { el, data }
let total = 0;
let done  = 0;
let activeSSE = null;

// ─── Başlangıç ───────────────────────────────────

checkHealth();

// ─── Sağlık Kontrolü ─────────────────────────────

async function checkHealth() {
    try {
        const res = await fetch(`${API_BASE}/health`, { signal: AbortSignal.timeout(4000) });
        const data = await res.json();

        dotLmstudio.className = 'health-dot ' + (data.lmstudio ? 'ok' : 'fail');
        dotComfyui.className  = 'health-dot ' + (data.comfyui ? 'ok' : 'fail');

        if (!data.lmstudio) {
            dotLmstudio.title = 'LM Studio çalışmıyor!';
        }
        if (!data.comfyui) {
            dotComfyui.title = 'ComfyUI çalışmıyor!';
        }
    } catch {
        dotLmstudio.className = 'health-dot fail';
        dotComfyui.className  = 'health-dot fail';
    }
}

// ─── Arama ───────────────────────────────────────

searchBtn.addEventListener('click', startSearch);
queryInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') startSearch();
});

function startSearch() {
    const query = queryInput.value.trim();
    if (!query) { queryInput.focus(); return; }

    // Önceki SSE varsa kapat
    if (activeSSE) { activeSSE.close(); activeSSE = null; }

    const count = parseInt(countSelect.value, 10);
    total = count;
    done  = 0;
    cards = {};

    // UI sıfırla
    galleryGrid.innerHTML = '';
    emptyState.style.display = 'none';
    progressZone.style.display = 'flex';
    progressFill.style.width   = '0%';
    progressLabel.textContent  = 'Aranıyor...';
    searchBtn.disabled = true;

    const url = `${API_BASE}/gallery-stream?query=${encodeURIComponent(query)}&count=${count}`;
    activeSSE = new EventSource(url);

    activeSSE.onmessage = (event) => {
        const msg = JSON.parse(event.data);
        handleSSEMessage(msg);
    };

    activeSSE.onerror = () => {
        progressLabel.textContent = 'Sunucu bağlantısı kesildi.';
        finalize();
    };
}

// ─── SSE Olay İşleyicisi ─────────────────────────

function handleSSEMessage(msg) {
    switch (msg.event) {
        case 'start':
            progressLabel.textContent = msg.message;
            total = msg.total;
            break;

        case 'progress':
            progressLabel.textContent = msg.message;
            updateProgress(msg.index, total);
            // Skeleton kart ekle
            if (!cards[msg.index]) {
                cards[msg.index] = { el: createSkeletonCard(msg.index), data: {} };
                galleryGrid.appendChild(cards[msg.index].el);
            }
            break;

        case 'original_ready': {
            // Skeleton yerine gerçek kartı başlat
            const entry = cards[msg.index];
            if (entry) {
                entry.data.original_url = msg.url;
                entry.data.title        = msg.title;
                populateCardOriginal(entry.el, msg.url, msg.title);
            }
            break;
        }

        case 'interpreted': {
            const entry = cards[msg.index];
            if (entry) {
                entry.data.quote = msg.quote;
                populateCardQuote(entry.el, msg.quote);
            }
            break;
        }

        case 'card_ready': {
            let entry = cards[msg.index];
            if (!entry) {
                entry = { el: createSkeletonCard(msg.index), data: {} };
                cards[msg.index] = entry;
                galleryGrid.appendChild(entry.el);
            }
            entry.data = { ...entry.data, ...msg };
            finalizeCard(entry.el, msg);
            done++;
            updateProgress(done, total);
            break;
        }

        case 'skip':
            done++;
            updateProgress(done, total);
            break;

        case 'error':
            progressLabel.textContent = '⚠ ' + msg.message;
            break;

        case 'done':
            progressLabel.textContent = msg.message;
            progressFill.style.width  = '100%';
            setTimeout(finalize, 1200);
            break;
    }
}

// ─── Kart Oluşturma ───────────────────────────────

function createSkeletonCard(index) {
    const card = document.createElement('div');
    card.className = 'card skeleton';
    card.dataset.index = index;
    card.innerHTML = `
        <div class="card-images loading"></div>
        <div class="card-body">
            <div class="card-quote"></div>
        </div>
    `;
    return card;
}

function populateCardOriginal(card, url, title) {
    card.classList.remove('skeleton');
    const imagesDiv = card.querySelector('.card-images');
    if (!imagesDiv) return;

    imagesDiv.classList.remove('loading');
    imagesDiv.innerHTML = `
        <img class="card-img original" src="${url}" alt="${title}" loading="lazy">
        <img class="card-img dylan" src="" alt="Dylan versiyonu" loading="lazy">
        <div class="sd-loading"><div class="spinner"></div></div>
    `;
}

function populateCardQuote(card, quote) {
    const quoteEl = card.querySelector('.card-quote');
    if (quoteEl) {
        quoteEl.textContent = quote;
        quoteEl.style.height = '';
        quoteEl.style.background = '';
        quoteEl.style.borderRadius = '';
    }
}

function finalizeCard(card, data) {
    card.classList.remove('skeleton');

    // Orijinal görsel
    const origImg = card.querySelector('.card-img.original');
    if (origImg && data.original_url) origImg.src = data.original_url;

    // Dylan versiyonu (SD çıktısı)
    const dylanImg = card.querySelector('.card-img.dylan');
    const sdLoading = card.querySelector('.sd-loading');

    if (dylanImg) {
        if (data.sd_url) {
            dylanImg.src = data.sd_url;
            dylanImg.onload = () => {
                if (sdLoading) sdLoading.style.display = 'none';
            };
        } else {
            // SD yoksa orijinali göster (filtreli)
            dylanImg.src = data.original_url || '';
            dylanImg.style.filter = 'sepia(0.6) contrast(1.1) brightness(0.85)';
            if (sdLoading) sdLoading.style.display = 'none';
        }
    }

    // Quote
    const quoteEl = card.querySelector('.card-quote');
    if (quoteEl && data.quote) {
        quoteEl.textContent = data.quote;
        quoteEl.style.cssText = '';
    }

    // Meta (kaynak)
    let metaEl = card.querySelector('.card-meta');
    if (!metaEl) {
        metaEl = document.createElement('div');
        metaEl.className = 'card-meta';
        card.querySelector('.card-body')?.appendChild(metaEl);
    }
    metaEl.innerHTML = `
        <span class="badge">Dylan AI</span>
        <span>${data.source || ''}</span>
    `;

    // Lightbox tıklama
    card.addEventListener('click', () => openLightbox(data));
}

// ─── Progress ─────────────────────────────────────

function updateProgress(current, total) {
    const pct = total > 0 ? Math.min(100, (current / total) * 100) : 0;
    progressFill.style.width = pct + '%';
}

// ─── Finalize ─────────────────────────────────────

function finalize() {
    searchBtn.disabled = false;
    if (galleryGrid.children.length === 0) {
        emptyState.style.display = 'block';
    }
    setTimeout(() => {
        progressZone.style.display = 'none';
    }, 2000);
    if (activeSSE) { activeSSE.close(); activeSSE = null; }
}

// ─── Lightbox ─────────────────────────────────────

function openLightbox(data) {
    lbOriginal.src = data.original_url || '';
    lbSd.src       = data.sd_url || data.original_url || '';
    if (!data.sd_url) {
        lbSd.style.filter = 'sepia(0.6) contrast(1.1) brightness(0.85)';
    } else {
        lbSd.style.filter = '';
    }
    lbQuote.textContent = data.quote || '';
    lightbox.classList.add('open');
    document.body.style.overflow = 'hidden';
}

function closeLightbox() {
    lightbox.classList.remove('open');
    document.body.style.overflow = '';
    lbOriginal.src = '';
    lbSd.src = '';
}

lightboxClose.addEventListener('click', closeLightbox);
lbBackdrop.addEventListener('click', closeLightbox);
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeLightbox();
});
