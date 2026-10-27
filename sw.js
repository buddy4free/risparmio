/* Buddy4Free Risparmio: copia locale dell'app per l'uso senza connessione */
const CACHE = 'b4f-202610271525';
const FILES = ["./", "index.html", "manifest.webmanifest", "fonts/fonts.css", "fonts/archivo.woff2", "fonts/figtree.woff2", "fonts/permanentmarker.woff2", "vendor/jspdf.umd.min.js", "icons/icon-192.png", "icons/icon-512.png", "icons/maskable-512.png", "icons/apple-touch-icon.png"];
self.addEventListener('install', e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES)).then(() => self.skipWaiting())); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(k => Promise.all(k.filter(x => x !== CACHE && x !== 'b4f-rem').map(x => caches.delete(x)))).then(() => self.clients.claim())); });
/* promemoria: al massimo una notifica al giorno, quando il telefono risveglia l'app (senza server) */
self.addEventListener('periodicsync', e => { if (e.tag === 'b4f-daily') e.waitUntil(daily()); });
async function daily(){
  const c = await caches.open('b4f-rem'), r = await c.match('rem.json'); if (!r) return; const s = await r.json(); if (!s.on) return;
  const now = new Date(), p2 = n => String(n).padStart(2, '0'), t = now.getFullYear() + '-' + p2(now.getMonth() + 1) + '-' + p2(now.getDate()), h = now.getHours();
  const sent = await c.match('sent.txt'); if (h < 8 || h >= 22 || (sent && await sent.text() === t)) return;
  let body = null, go = 'home';
  if (s.quiz !== t) { body = 'La domanda del giorno ti aspetta: un minuto.'; go = 'learn'; }
  else if (s.gymN && s.gym !== t) { body = 'Tappa ' + s.gymN + ' della palestra del risparmio.'; go = 'gym'; }
  else if (s.track !== t && h >= 19) { body = 'Hai segnato tutto oggi? Un controllo veloce.'; go = 'tx'; }
  if (!body) return;
  await c.put('sent.txt', new Response(t));
  return self.registration.showNotification('Buddy4Free Risparmio', {body, icon:'icons/icon-192.png', badge:'icons/icon-192.png', tag:'b4f-daily', data:{go}});
}
self.addEventListener('notificationclick', e => { e.notification.close(); const go = (e.notification.data || {}).go || 'home';
  e.waitUntil(clients.matchAll({type:'window', includeUncontrolled:true}).then(L => { for (const w of L) { w.postMessage({go}); return w.focus(); } return clients.openWindow('./?go=' + go); })); });
self.addEventListener('fetch', e => {
  const r = e.request; if (r.method !== 'GET' || new URL(r.url).origin !== location.origin) return;
  /* la pagina dell'app: prima la versione più recente dalla rete, se non c'è connessione quella salvata */
  if (r.mode === 'navigate') { e.respondWith(fetch(r).then(res => { const copy = res.clone(); caches.open(CACHE).then(c => c.put('index.html', copy)); return res; }).catch(() => caches.match('index.html'))); return; }
  e.respondWith(caches.match(r, {ignoreSearch:true}).then(hit => {
    const net = fetch(r).then(res => { if (res.ok) { const copy = res.clone(); caches.open(CACHE).then(c => c.put(r, copy)); } return res; }).catch(() => hit || caches.match('index.html'));
    return hit || net;
  }));
});
