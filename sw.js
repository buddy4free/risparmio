/* Buddy4Free Risparmio: copia locale dell'app per l'uso senza connessione */
const CACHE = 'b4f-202610251207';
const FILES = ["./", "index.html", "manifest.webmanifest", "fonts/fonts.css", "fonts/archivo.woff2", "fonts/figtree.woff2", "fonts/permanentmarker.woff2", "vendor/jspdf.umd.min.js", "icons/icon-192.png", "icons/icon-512.png", "icons/maskable-512.png", "icons/apple-touch-icon.png"];
self.addEventListener('install', e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES)).then(() => self.skipWaiting())); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(k => Promise.all(k.filter(x => x !== CACHE).map(x => caches.delete(x)))).then(() => self.clients.claim())); });
self.addEventListener('fetch', e => {
  const r = e.request; if (r.method !== 'GET' || new URL(r.url).origin !== location.origin) return;
  /* la pagina dell'app: prima la versione più recente dalla rete, se non c'è connessione quella salvata */
  if (r.mode === 'navigate') { e.respondWith(fetch(r).then(res => { const copy = res.clone(); caches.open(CACHE).then(c => c.put('index.html', copy)); return res; }).catch(() => caches.match('index.html'))); return; }
  e.respondWith(caches.match(r, {ignoreSearch:true}).then(hit => {
    const net = fetch(r).then(res => { if (res.ok) { const copy = res.clone(); caches.open(CACHE).then(c => c.put(r, copy)); } return res; }).catch(() => hit || caches.match('index.html'));
    return hit || net;
  }));
});
