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

## Da fare prima dell'uscita pubblica
- Copia locale (service worker): tenere caratteri, libreria PDF, icone e motore scontrini in una cache stabile, per non riscaricarli a ogni aggiornamento. Rimandato perché tocca il meccanismo degli aggiornamenti: va provato bene, compreso il passaggio dalla versione precedente.
- Soluzione Android definitiva, non legata al browser (vedi `store/ANDROID.md`).

## Linguaggio dei testi (coach, suggerimenti, obiettivi)
- Mai frasi che sembrino consigli finanziari o ordini ("fai questo", "sposta questo", "riduci", "imposta un bonifico"): l'app descrive i dati e le conseguenze ("al ritmo attuale…", "servirebbero…", "con il 30% in meno…"), la scelta resta all'utente.
- I numeri del mese in corso sono reali a oggi; i movimenti programmati compaiono solo come previsione, dichiarata come tale.

## Dove stanno le cose
- Sorgente unica: `sorgente/fin-app.html` → `python3 sorgente/build_pwa.py` genera `index.html` e `sw.js`.
- Pacchetto Android e rilasci: `android/`, `store/ANDROID.md`, workflow `.github/workflows/android.yml`.
- Testi Play Store e tester: `store/SCHEDA-PLAY.md`, `store/POST-TESTER.md`.
- Mai inserire nel repository chiavi, keystore o password; non usare l'email personale di Lorenzo (usare buddyforfree@gmail.com).
