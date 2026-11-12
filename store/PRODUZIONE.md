# Richiesta di accesso alla produzione (Play Console) · bozza delle risposte

Preparata il 12/11/2026 dalle pubblicazioni del test chiuso (issue GitHub #1–#16). Le parti tra [ ] le completa Lorenzo.
Le risposte vanno scritte in modo veritiero: niente riscontri inventati.

## 1. Il test chiuso

**Quanto è stato facile reclutare i tester?**
[Scegliere: Molto facile / Facile / Né facile né difficile / Difficile / Molto difficile]

**Descrivi il coinvolgimento dei tester durante il test chiuso.**
I tester hanno usato l'app ogni giorno con i propri dati reali (entrate, spese, obiettivi di risparmio), non con dati di prova. Hanno registrato movimenti, importato storici da file CSV, usato il backup cifrato, i grafici e la revisione mensile. Per raccogliere i problemi abbiamo aggiunto nell'app la funzione "Segnala un problema", che prepara i dettagli tecnici da inviare senza dati finanziari; le segnalazioni ricevute ci hanno permesso di trovare e correggere problemi reali di stabilità e velocità. Durante i 14 giorni abbiamo pubblicato 16 aggiornamenti, ciascuno con un messaggio ai tester sulle novità. [Aggiungere: numero di tester attivi e come vi siete sentiti con loro, es. gruppo WhatsApp / email.]

**Riepiloga i feedback ricevuti e come li hai raccolti.**
Feedback raccolti tramite la funzione "Segnala un problema" nell'app, messaggi diretti [e il questionario finale di 3 domande]. I temi principali:
- stabilità all'apertura (in un caso l'app restava sul logo) e un pulsante che non rispondeva;
- reattività: tastierina dell'importo e pulsante Salva percepiti in ritardo, rallentamenti con storici molto grandi (oltre 6.000 movimenti);
- aggiornamenti: alcuni telefoni restavano una versione indietro;
- usabilità: movimenti programmati mescolati a quelli reali, errori della password del backup poco visibili, saldi di inizio mese da inserire due volte;
- contenuti: suggerimenti troppo generici o non pertinenti ai dati dell'utente;
- funzioni richieste: previsione del mese prima dell'arrivo dello stipendio.
[Aggiungere i riscontri dei tester al questionario finale.]

## 2. L'app

**Chi è il pubblico di destinazione?**
Adulti in Italia che vogliono capire dove vanno i propri soldi e risparmiare con un metodo semplice, senza collegare il conto bancario e senza che i dati lascino il telefono. È rivolta in particolare al pubblico del canale di educazione finanziaria Buddy4Free.

**Descrivi come l'app offre valore agli utenti.**
Buddy4Free Risparmio è un'app gratuita, senza pubblicità e senza account, che aiuta a tenere traccia di entrate e spese, a vedere il proprio tasso di risparmio e a organizzare i soldi in 4 "pilastri" (liquidità, fondo di emergenza, obiettivi, investimenti). Offre grafici, una revisione mensile guidata, un simulatore di interesse composto e inflazione, obiettivi di risparmio con previsione dei tempi, una palestra del risparmio con lezioni brevi e un indice di benessere finanziario. Tutti i dati restano sul telefono dell'utente; il backup è cifrato con una password scelta dall'utente. L'app descrive i dati e le conseguenze, non dà consigli finanziari.

**Quante installazioni prevedi nel primo anno?**
[Scegliere la fascia, es. 1.000–10.000, in base al pubblico del canale.]

## 3. Preparazione per la produzione

**Quali modifiche hai apportato all'app in base a quanto appreso durante il test chiuso?**
- Modalità sicura all'avvio: se un'apertura si blocca, la successiva offre di riprovare, salvare una copia dei dati e inviare i dettagli dell'errore.
- Funzione "Segnala un problema" con diagnostica senza dati finanziari, e avviso automatico alla riapertura dopo un blocco.
- Aggiornamenti affidabili: nessun telefono resta indietro di una versione; avviso "È pronta una nuova versione".
- Reattività: tasti e pulsante Salva rispondono al tocco; navigazione e disegno più leggeri con storici molto grandi.
- Usabilità: movimenti programmati separati in fondo alla lista, errori del backup mostrati subito, apertura sempre dalla Home, allineamento automatico dei saldi di inizio mese.
- Nuova funzione richiesta: "Il mio stipendio", con la previsione del mese prima dell'accredito (anche per due stipendi o una pensione).
- Suggerimenti, coach e revisione mensile resi personalizzati sui dati reali dell'utente, solo con informazioni pertinenti.
- Tema chiaro e scuro che segue il telefono, guida completa nell'app.

**Come hai deciso che l'app è pronta per la produzione?**
Tutti i problemi segnalati durante il test sono stati corretti e verificati, anche con dati di grandi dimensioni (oltre 6.000 movimenti). Ogni pubblicazione passa da test di sicurezza automatici (backup con dati malevoli, cifratura, blocco con PIN, protezione dei contenuti) e da un controllo che blocca modifiche non previste. Negli ultimi giorni del test non sono emersi errori bloccanti. [Aggiungere: i riscontri finali dei tester.] Prima del rilascio pubblico verrà pubblicata una versione Android con motore interno, provata prima su un dispositivo di test.

## Versioni brevi (massimo 300 caratteri, richieste dal modulo)

**Coinvolgimento dei tester** (280 caratteri)
I tester hanno usato l'app ogni giorno con i propri dati reali: movimenti, import CSV, backup, grafici, revisione mensile. Con la funzione "Segnala un problema" ci hanno mandato dettagli tecnici. In 14 giorni abbiamo pubblicato 16 aggiornamenti, ognuno con un messaggio ai tester.

**Riepilogo dei feedback** (255 caratteri)
Raccolti con "Segnala un problema" nell'app e messaggi diretti. Temi: blocco all'apertura, tasti e Salva lenti, rallentamenti con oltre 6.000 movimenti, aggiornamenti in ritardo, suggerimenti poco pertinenti, richiesta di previsione prima dello stipendio.

**Pubblico di destinazione** (241 caratteri)
Adulti in Italia che vogliono capire dove vanno i propri soldi e risparmiare con un metodo semplice, senza collegare il conto e senza che i dati lascino il telefono. In particolare il pubblico del canale di educazione finanziaria Buddy4Free.

**Valore per gli utenti** (281 caratteri)
App gratuita, senza pubblicità né account: registra entrate e spese, mostra il tasso di risparmio, organizza i soldi in 4 pilastri, con obiettivi, grafici, revisione mensile, simulatore e lezioni brevi. I dati restano sul telefono, backup cifrato. Descrive i dati, non dà consigli.

**Modifiche dopo il test** (272 caratteri)
Modalità sicura all'avvio, "Segnala un problema", aggiornamenti senza ritardi, tasti e Salva più reattivi, app più veloce con molti dati, movimenti programmati separati, saldi allineati in automatico, previsione dello stipendio, suggerimenti personalizzati sui dati reali.

**Come hai deciso che è pronta** (235 caratteri)
Tutti i problemi segnalati sono stati corretti e verificati anche con oltre 6.000 movimenti. Ogni pubblicazione passa test di sicurezza automatici (backup, cifratura, PIN). Negli ultimi giorni del test non sono emersi errori bloccanti.

