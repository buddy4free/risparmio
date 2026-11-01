#!/usr/bin/env python3
"""Costruisce l'anteprima per l'artifact di Lorenzo (non per i tester): loghi dentro la pagina e
lezioni, tappe e domande del giorno tutte aperte. Uso: python3 sorgente/anteprima.py /percorso/uscita.html
Poi si pubblica sull'artifact https://claude.ai/artifact/SKGYXcdzEhsYz7Btngm8hq (slug cd016ef5-7c8d-4056-a471-679ff234f26c)."""
import json, os, sys
D = os.path.dirname(os.path.abspath(__file__)) + '/'
L = json.load(open(D + 'logo.json')); s = open(D + 'fin-app.html').read()
for k, v in [('__ENSO__', L.get('enso', '')), ('__WORD__', L.get('word', '')), ('__FULL__', L.get('full', ''))]: s = s.replace(k, v)
assert s.count('const PREVIEW = false;') == 1; s = s.replace('const PREVIEW = false;', 'const PREVIEW = true;')
open(sys.argv[1], 'w').write(s); print('anteprima scritta in', sys.argv[1])
