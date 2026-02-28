// ═══════════════════════════════════════════════════════
//  QR Attendance — Service Worker
//  Cache-first strategy. Bump CACHE_NAME to force update.
// ═══════════════════════════════════════════════════════
const CACHE_NAME = 'qr-attendance-v1';

const FILES_TO_CACHE = [
  './Scanner.html',
  './manifest.json',
  './sw.js',
  './icon-192.png',
  './icon-512.png',
];

// ── INSTALL: cache all files ─────────────────────────────
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(FILES_TO_CACHE))
      .then(() => self.skipWaiting())
  );
});

// ── ACTIVATE: delete old caches ──────────────────────────
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(
        keys
          .filter(k => k !== CACHE_NAME)
          .map(k => caches.delete(k))
      ))
      .then(() => self.clients.claim())
  );
});

// ── FETCH: cache-first, network fallback ─────────────────
self.addEventListener('fetch', event => {
  // Only handle GET requests
  if (event.request.method !== 'GET') return;

  event.respondWith(
    caches.match(event.request)
      .then(cached => {
        if (cached) return cached;
        // Not in cache — fetch from network (only needed online)
        return fetch(event.request)
          .then(response => {
            // Cache valid responses dynamically (e.g. icon loaded late)
            if (response && response.status === 200 && response.type === 'basic') {
              const clone = response.clone();
              caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
            }
            return response;
          });
      })
  );
});
