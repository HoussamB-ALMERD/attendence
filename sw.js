// ═══════════════════════════════════════════════════════
//  QR Attendance — Service Worker
//  Cache-first strategy. Bump CACHE_NAME to force update.
// ═══════════════════════════════════════════════════════
const CACHE_NAME = 'qr-attendance-v6';

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

// ── FETCH ────────────────────────────────────────────────
// Scanner.html: network-first so updates reach the phone automatically.
// Everything else: cache-first (icons, manifest, sw.js never change mid-session).
self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET') return;

  const url = new URL(event.request.url);
  const isMainPage = url.pathname.endsWith('Scanner.html') || url.pathname.endsWith('/');

  if (isMainPage) {
    // Network-first: try to fetch latest, fall back to cache when offline
    event.respondWith(
      fetch(event.request)
        .then(response => {
          if (response && response.status === 200) {
            const clone = response.clone();
            caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
          }
          return response;
        })
        .catch(() => caches.match(event.request))
    );
  } else {
    // Cache-first for all other static assets
    event.respondWith(
      caches.match(event.request)
        .then(cached => cached || fetch(event.request))
    );
  }
});
