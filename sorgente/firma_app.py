"""Aggiornamenti firmati per l'app Android definitiva.

Crea app/aggiornamento.json (versione della pagina e impronta SHA-256 di ogni file) e lo firma con la chiave privata
di Lorenzo (secret B4F_FIRMA_PRIVATA, ECDSA P-256). L'app accetta un aggiornamento solo se la firma corrisponde alla
chiave pubblica che porta con sé e se ogni file scaricato ha l'impronta indicata qui.
Senza la chiave (per esempio in prova) non firma e non pubblica nulla per l'app.
"""
import hashlib, json, os, re, subprocess, sys, tempfile, glob

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
chiave = os.environ.get('B4F_FIRMA_PRIVATA', '').strip()
if not chiave:
    print('::warning::Manca B4F_FIRMA_PRIVATA: nessun aggiornamento firmato per l\'app Android')
    sys.exit(0)
html = open(D + 'index.html', encoding='utf-8').read()
ver = re.search(r'name="b4f-build" content="(\d+)"', html).group(1)
nativo = int(open(D + 'sorgente/nativo.txt').read().strip())
# i file della pagina che cambiano con le pubblicazioni (guida e lettore scontrini restano quelli inclusi nell'app)
files = ['index.html', 'manifest.webmanifest', 'vendor/jspdf.umd.min.js'] + sorted(glob.glob('fonts/*', root_dir=D)) + sorted(glob.glob('icons/*', root_dir=D))
imp = {f: hashlib.sha256(open(D + f, 'rb').read()).hexdigest() for f in files if os.path.isfile(D + f)}
os.makedirs(D + 'app', exist_ok=True)
dati = json.dumps({'ver': ver, 'nativo': nativo, 'files': imp}, sort_keys=True, separators=(',', ':')).encode()
open(D + 'app/aggiornamento.json', 'wb').write(dati)
with tempfile.TemporaryDirectory() as t:
    k = t + '/k.pem'
    with open(k, 'w') as fh:
        fh.write(chiave if chiave.endswith('\n') else chiave + '\n')
    os.chmod(k, 0o600)
    firma = subprocess.run(['openssl', 'dgst', '-sha256', '-sign', k, D + 'app/aggiornamento.json'], check=True, capture_output=True).stdout
import base64
open(D + 'app/aggiornamento.sig', 'w').write(base64.b64encode(firma).decode())
print('Aggiornamento firmato per l\'app: versione %s, %d file, nativo %d' % (ver, len(imp), nativo))
