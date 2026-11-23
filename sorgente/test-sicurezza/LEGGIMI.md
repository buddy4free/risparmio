# Test di sicurezza

Attacchi automatici all'app, da rilanciare a ogni aggiornamento.

```
sh sorgente/test-sicurezza/esegui.sh
```

Servono Node e Playwright con Chromium. Lo script ricostruisce l'app, la serve su `localhost:8767` e lancia i test. Ogni riga dice OK o FAIL; alla fine c'è il riepilogo.

| File | Cosa prova |
|---|---|
| `01-backup-avvelenato.js` | Backup malevolo con codice in ogni campo (testi, codici, numeri, date, colori), ripristino, clic su tutte le schermate, CSV e PDF |
| `02-csp-file-cifratura.js` | Blocco del codice iniettato e dell'invio di dati ad altri siti, CSV malevolo, formule nel CSV esportato, backup cifrato manomesso, memoria del telefono avvelenata |
| `03-blocco-pin.js` | "Richiedi dopo", PIN sbagliati ripetuti anche riaprendo l'app, tastiera e tasto indietro sotto il blocco, backup che porta un altro PIN, impronta |
| `04-cornice.js` | L'app non si apre dentro la pagina di un altro sito |
| `05-flussi.js` | Flussi di tutti i giorni: aggiungere un'uscita dal tasto + (categoria, sottocategoria, tastierina, nota), backup protetto e ripristino completo, import CSV, apertura di tutte le schermate e delle Impostazioni senza errori |
| `06-gesti.js` | Gesti col dito su un telefono simulato (scorrere sopra il grafico, girare il cerchio, cambiare scheda, finestra veloce, fumetti delle novità) e col mouse (trascinare le schede) |

I file generati durante le prove finiscono in `out/`, che non va nel repository.

Nuovi attacchi: aggiungere un file `05-....js` che usa `comune.js` (`apri`, `demo`, `ok`, `fine`).
