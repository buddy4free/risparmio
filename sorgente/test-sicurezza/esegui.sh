#!/bin/sh
# Ricostruisce l'app e lancia tutti i test di sicurezza. Uso: sh sorgente/test-sicurezza/esegui.sh
cd "$(dirname "$0")/../.." || exit 1
python3 sorgente/build_pwa.py || exit 1
PORT=8767
if ! curl -s -o /dev/null "http://localhost:$PORT/"; then (setsid nohup python3 -m http.server $PORT >/dev/null 2>&1 &); sleep 1; fi
esito=0
for t in sorgente/test-sicurezza/0*.js; do
  echo "=== $(basename "$t")"
  node "$t" || esito=1
done
[ $esito = 0 ] && echo "\nSICUREZZA: tutto superato" || echo "\nSICUREZZA: ci sono prove fallite"
exit $esito
