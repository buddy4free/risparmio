#!/usr/bin/env python3
"""Guardiano della pubblicazione: gira prima di ogni pubblicazione e la blocca se qualcosa
che non dovrebbe mai cambiare è cambiato. Protegge dagli attacchi automatici o frettolosi
(per esempio un account rubato che inietta codice), non da chi conosce e modifica anche questo file.

Uso:  python3 sorgente/guardiano.py            controlla index.html, sw.js e le librerie
      python3 sorgente/guardiano.py --aggiorna   ricalcola le impronte delle librerie (solo dopo
                                                 averle aggiornate di proposito)"""
import hashlib, json, os, re, sys

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
IMPRONTE = D + 'sorgente/guardiano-impronte.json'
LIBRERIE = ['vendor/jspdf.umd.min.js', 'vendor/ocr/tesseract.min.js', 'vendor/ocr/worker.min.js',
            'vendor/ocr/tesseract-core-lstm.wasm.js', 'vendor/ocr/tesseract-core-simd-lstm.wasm.js',
            'vendor/ocr/ita.traineddata.gz', 'fonts/fonts.css', 'fonts/archivo.woff2', 'fonts/figtree.woff2',
            'fonts/permanentmarker.woff2']
# la regola di sicurezza della pagina: deve restare esattamente questa (cambia solo l'impronta dello script)
CSP = ("default-src 'self'; script-src 'self' 'sha256-*'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; "
       "font-src 'self' data:; media-src 'self' data: blob:; connect-src 'self'; worker-src 'self'; manifest-src 'self'; "
       "object-src 'none'; frame-src 'none'; base-uri 'none'; form-action 'none'")
# siti esterni che l'app può solo aprire come link (nessun dato viene inviato)
SITI = {'calendar.google.com', 'www.youtube.com', 'youtube.com', 'www.garanteprivacy.it', 'buddy4free.github.io'}
VIETATI = ['eval(', 'new Function', 'sendBeacon', 'WebSocket', 'EventSource', 'importScripts', 'XMLHttpRequest',
           'document.write', 'setTimeout("', "setTimeout('", 'setInterval("', "setInterval('"]

def impronta(f):
    return hashlib.sha256(open(D + f, 'rb').read()).hexdigest()

if '--aggiorna' in sys.argv:
    json.dump({f: impronta(f) for f in LIBRERIE}, open(IMPRONTE, 'w'), indent=1)
    print('Impronte aggiornate:', len(LIBRERIE)); sys.exit(0)

err = []
page, sw = open(D + 'index.html').read(), open(D + 'sw.js').read()
m = re.findall(r'http-equiv="Content-Security-Policy" content="([^"]*)"', page)
if len(m) != 1: err.append('regola di sicurezza (CSP) mancante o doppia nella pagina')
elif re.sub(r"'sha256-[A-Za-z0-9+/=]+'", "'sha256-*'", m[0]) != CSP: err.append('regola di sicurezza (CSP) cambiata: ' + m[0])
if page.count('<script') != 1: err.append('la pagina deve avere un solo script')
for nome, testo in (('index.html', page), ('sw.js', sw)):
    for v in VIETATI:
        if v in testo: err.append(nome + ': compare "' + v + '"')
    for h in sorted(set(re.findall(r'https?://([A-Za-z0-9.-]+)', testo))):
        if h not in SITI: err.append(nome + ': indirizzo esterno non previsto ' + h)
    if re.search(r"fetch\(\s*['\"`]https?:", testo): err.append(nome + ': richiesta verso un sito esterno')
for src in re.findall(r"loadScript\('([^']*)'\)", page):
    if not src.startswith('vendor/'): err.append('script caricato da fuori dalle librerie: ' + src)
if "OCR_PATH = 'vendor/ocr/'" not in page and "OCR_PATH = ''" not in page: err.append('percorso del motore scontrini cambiato')
try: attese = json.load(open(IMPRONTE))
except Exception: attese = {}; err.append('impronte delle librerie mancanti')
for f, h in attese.items():
    if not os.path.exists(D + f): err.append('libreria mancante: ' + f)
    elif impronta(f) != h: err.append('libreria modificata: ' + f)
if err:
    print('GUARDIANO: pubblicazione bloccata')
    for e in err: print('::error::' + e)
    sys.exit(1)
print('GUARDIANO: tutto in ordine')
