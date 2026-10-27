# Buddy4Free Risparmio · regole di lavoro

## Fase attuale: test chiuso con tester reali (dal 26/10/2026)
L'app è installata dai tester tramite Play Store (test chiuso) e usa i loro dati veri.
Ogni modifica pubblicata sul sito arriva **subito** a tutti i tester.

Prima di qualsiasi modifica sostanziale (dati salvati, calcoli, struttura delle schermate, flussi, notifiche, backup, PIN, pacchetto Android):
1. **Valutare e dire a Lorenzo gli impatti sui tester prima di farla**: dati esistenti, backup già fatti, abitudini d'uso, cosa vedranno di diverso.
2. Le modifiche devono restare **compatibili con i dati già salvati** e con i backup vecchi (niente perdita o reinterpretazione silenziosa dei dati).
3. Se cambia qualcosa che i tester notano, proporre un breve messaggio da mandare loro.
4. Le modifiche al pacchetto Android (icona, browser, nome) richiedono una nuova versione sul Play Store: raggrupparle (vedi `store/ANDROID.md`).
5. Prima di pubblicare: test di sicurezza (`sh sorgente/test-sicurezza/esegui.sh`) e prova del flusso toccato.

## Pubblicazioni raggruppate (deciso il 27/10/2026)
- Le modifiche si fanno sul ramo `prossima`, non su `main`: `main` è il sito che arriva subito ai tester.
- L'artifact si aggiorna subito come anteprima per Lorenzo.
- La pubblicazione è automatica: il workflow `.github/workflows/pubblica.yml` alle 06:30 e alle 13:30 (ora italiana d'inverno) unisce `prossima` in `main`, ricostruisce, lancia i test di sicurezza e pubblica solo se passano. Si può lanciare anche a mano quando Lorenzo dice "pubblica".
- Le novità che i tester noteranno si scrivono in `store/NOVITA.md` (una riga "- " per novità): alla pubblicazione diventano una issue con il messaggio pronto per i tester.
- Eccezione: correzioni urgenti (errori che bloccano l'app o rischi sui dati) si pubblicano subito, dicendolo a Lorenzo.

## Da fare il 28/10/2026 (sicurezza della pubblicazione)
Ordine deciso con Lorenzo: 1) verifica in due passaggi sui suoi account (15 minuti, guidato); 2) tema chiaro (sezione più sotto); 3) guardiano, avviso a ogni pubblicazione e protezione di `main`.
- Guidare Lorenzo ad attivare la verifica in due passaggi (meglio passkey) su GitHub, account Google (Gmail Buddy4Free e Play Console) e Claude, e a controllare le sessioni attive su GitHub.
- "Guardiano" nel workflow `pubblica.yml`: blocca la pubblicazione se la CSP viene allentata, se compaiono indirizzi esterni a cui spedire dati o codice eseguito al volo (eval, new Function).
- Avviso (issue) a ogni pubblicazione, non solo quando ci sono novità per i tester.
- Guidare Lorenzo a proteggere il ramo `main` su GitHub (niente force push), verificando che la pubblicazione automatica continui a funzionare.

## In coda dopo la sicurezza: tema chiaro (scelte di Lorenzo del 27/10/2026)
- Opzione in Impostazioni → Visualizzazione: Scuro / Chiaro / Come il telefono; predefinito Scuro (per i tester non cambia nulla finché non scelgono).
- Chiaro: sfondo bianco caldo (#F5F4EF), schede bianche con bordo leggero, testo quasi nero; giallo Buddy4Free per pulsanti, + e bordo della scheda principale; verdi/arancioni/rossi un po' più scuri.
- Logo nel tondo nero (cerchio giallo + BUDDY + 4 FREE, come sulla maglietta); "Risparmio" in alto in ambra (#9A6A00); icone in alto nere.
- Barra in basso: voce attiva con icona nera dentro una pillola gialla piena (come il +), scritta nera in grassetto; le altre grigie.
- Da rifinire: grafici, illustrazioni, PDF, immagini della guida anche in versione chiara. Prova di riferimento: script `light.js` nello scratchpad della sessione del 27/10.

## Da fare prima dell'uscita pubblica
- Copia locale (service worker): tenere caratteri, libreria PDF, icone e motore scontrini in una cache stabile, per non riscaricarli a ogni aggiornamento. Rimandato perché tocca il meccanismo degli aggiornamenti: va provato bene, compreso il passaggio dalla versione precedente.
- Soluzione Android definitiva, non legata al browser (vedi `store/ANDROID.md`).
- Notifiche vere (programmate, native) con l'app Android definitiva: deciso il 27/10/2026, niente server di notifiche nel frattempo.

## Linguaggio dei testi (coach, suggerimenti, obiettivi)
- Mai frasi che sembrino consigli finanziari o ordini ("fai questo", "sposta questo", "riduci", "imposta un bonifico"): l'app descrive i dati e le conseguenze ("al ritmo attuale…", "servirebbero…", "con il 30% in meno…"), la scelta resta all'utente.
- I numeri del mese in corso sono reali a oggi; i movimenti programmati compaiono solo come previsione, dichiarata come tale.

## Dove stanno le cose
- Sorgente unica: `sorgente/fin-app.html` → `python3 sorgente/build_pwa.py` genera `index.html` e `sw.js`.
- Pacchetto Android e rilasci: `android/`, `store/ANDROID.md`, workflow `.github/workflows/android.yml`.
- Testi Play Store e tester: `store/SCHEDA-PLAY.md`, `store/POST-TESTER.md`.
- Mai inserire nel repository chiavi, keystore o password; non usare l'email personale di Lorenzo (usare buddyforfree@gmail.com).
