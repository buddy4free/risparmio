# Buddy4Free Risparmio

App gratuita per la finanza personale del canale [Buddy4Free](https://www.youtube.com/@Buddy4Free): entrate e uscite, i 4 pilastri, obiettivi, sfide, lezioni e benessere.

- App: https://buddy4free.github.io/risparmio/
- [Termini e condizioni](https://buddy4free.github.io/risparmio/terms.html) · [Informativa sulla privacy](https://buddy4free.github.io/risparmio/privacy.html)

## Struttura

- `index.html`, `sw.js`, `manifest.webmanifest`: l'app installabile, funziona anche offline.
- `fonts/`, `vendor/`, `icons/`: caratteri, libreria PDF e icone inclusi nell'app.
- `privacy.html`, `terms.html`: le pagine legali, generate dai testi dell'app.
- `sorgente/`: il file di lavoro (`fin-app.html`) e gli script che producono l'app (`build_pwa.py`, `gen_legal.js`).
