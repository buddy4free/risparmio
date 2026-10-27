import json,re,os,time,shutil
import os
_HERE=os.path.dirname(os.path.abspath(__file__))
P=os.environ.get('B4F_SRC',_HERE+'/')
D=os.path.dirname(_HERE)+'/'
s=open(P+'fin-app.html').read()
L=json.load(open(P+'logo.json'))
for k in ['ENSO','WORD','FULL']: s=s.replace('__'+k+'__',L[k.lower()])
def rep(a,b,cnt=1):
    global s
    n=s.count(a); assert n==cnt,(n,a[:80]); s=s.replace(a,b)
VER=time.strftime('%Y%m%d%H%M')
# caratteri inclusi
i=s.index('<link rel="preconnect" href="https://fonts.googleapis.com">'); j=s.index('<style>',i)
s=s[:i]+'<link rel="stylesheet" href="fonts/fonts.css">\n'+s[j:]
open(D+'fonts/fonts.css','w').write(open(P+'fontface.css').read())
# PDF incluso
rep("loadScript('https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js')","loadScript('vendor/jspdf.umd.min.js')")
# lettore degli scontrini incluso (vendor/ocr), attivo solo nell'app installata
rep("const OCR_PATH = '';","const OCR_PATH = 'vendor/ocr/';")
# link dell'app = indirizzo del sito
rep("APP_URL = 'https://claude.ai/artifact/SKGYXcdzEhsYz7Btngm8hq'","APP_URL = location.origin + location.pathname.replace(/index\\.html$/, '')")
rep('value="https://claude.ai/artifact/SKGYXcdzEhsYz7Btngm8hq"','value="\' + APP_URL + \'"')
rep("Per invitare un amico, condividi l\\'app dal menu Condividi di questa pagina, poi mandagli il link. Ognuno vede solo i propri dati.","Per invitare un amico mandagli questo link. Ognuno vede solo i propri dati, salvati sul proprio telefono.")
# salvataggio file senza la piattaforma claude.ai
rep("let remote = null, writing = false, pending = false, saveTimer = null, downloads = null;",
"""let remote = null, writing = false, pending = false, saveTimer = null, downloads = {save:async ({filename, data}) => {
  const blob = data instanceof Blob ? data : new Blob([data], {type:/\\.json$/.test(filename) ? 'application/json' : /\\.csv$/.test(filename) ? 'text/csv' : 'application/octet-stream'});
  const f = new File([blob], filename, {type:blob.type});
  const mob = /Android|iPhone|iPad/.test(navigator.userAgent), alt = /\\.json$/.test(filename) ? new File([blob], filename.replace(/\\.json$/, '.txt'), {type:'text/plain'}) : null;
  for (const ff of [f, alt]) if (ff && mob && navigator.canShare && navigator.canShare({files:[ff]})) { try { await navigator.share({files:[ff], title:filename}); return; } catch(e) { if (e && e.name === 'AbortError') throw {code:'declined'}; } }
  const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = filename; document.body.appendChild(a); a.click(); setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 1000);
}};""")
head='''<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#000000">
<meta name="color-scheme" content="dark only">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; font-src 'self' data:; media-src 'self' data: blob:; connect-src 'self'; worker-src 'self'; manifest-src 'self'; object-src 'none'; frame-src 'none'; base-uri 'none'; form-action 'none'">
<meta name="referrer" content="no-referrer">
<meta name="darkreader-lock">
<meta name="description" content="Buddy4Free Risparmio: traccia entrate e uscite, riempi i 4 pilastri e raggiungi i tuoi obiettivi. Gratuita, senza pubblicità.">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" href="icons/icon-192.png">
<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
<style>html,body{margin:0;background:#000}</style>
'''
assert s.count('</script>')==1, 'script'
s=head+s.replace('</script>','''/* app installabile: funziona anche offline */
if ('serviceWorker' in navigator) window.addEventListener('load', () => navigator.serviceWorker.register('sw.js').catch(() => {}));
if (navigator.storage && navigator.storage.persist) navigator.storage.persist().catch(() => {});
</script>''',1)
# il corpo: title e style restano, chiudiamo head prima del primo elemento visibile
k=s.index('</style>', s.index('<style>', len(head)))+len('</style>')
s=s[:k]+'\n</head>\n<body>'+s[k:]+'\n</body>\n</html>\n'
# l'app non si apre dentro pagine di altri siti (clickjacking)
s=s.replace('<script>','<script>\nif (window.top !== window.self) { try { top.location = location.href; } catch(e) {} document.documentElement.innerHTML = \'\'; throw new Error(\'frame\'); }',1)
# CSP: si esegue solo lo script dell'app (impronta SHA-256), nessun codice iniettato
import hashlib,base64
i=s.index('<script>')+len('<script>'); j=s.index('</script>',i); assert s.count('<script')==1
h=base64.b64encode(hashlib.sha256(s[i:j].encode()).digest()).decode()
s=s.replace("script-src 'self' 'unsafe-inline'","script-src 'self' 'sha256-%s'"%h,1)
open(D+'index.html','w').write(s)
json.dump({"name":"Buddy4Free Risparmio","short_name":"Buddy4Free","description":"Traccia entrate e uscite, riempi i 4 pilastri e raggiungi i tuoi obiettivi. Gratuita, senza pubblicità.","lang":"it","start_url":"./","scope":"./","display":"standalone","orientation":"portrait","background_color":"#000000","theme_color":"#000000","categories":["finance","education","lifestyle"],
  "icons":[{"src":"icons/icon-192.png","sizes":"192x192","type":"image/png"},{"src":"icons/icon-512.png","sizes":"512x512","type":"image/png"},{"src":"icons/maskable-512.png","sizes":"512x512","type":"image/png","purpose":"maskable"}]},open(D+'manifest.webmanifest','w'),ensure_ascii=False,indent=2)
files=['./','index.html','manifest.webmanifest','fonts/fonts.css','fonts/archivo.woff2','fonts/figtree.woff2','fonts/permanentmarker.woff2','vendor/jspdf.umd.min.js','icons/icon-192.png','icons/icon-512.png','icons/maskable-512.png','icons/apple-touch-icon.png']
open(D+'sw.js','w').write('''/* Buddy4Free Risparmio: copia locale dell'app per l'uso senza connessione */
const CACHE = 'b4f-%s';
const FILES = %s;
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
'''%(VER,json.dumps(files)))
open(D+'.nojekyll','w').write('')
print('build',VER,len(s))
