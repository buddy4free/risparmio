# Fase 4 · l'app definitiva sul test chiuso (preparato il 17/11/2026)

L'app definitiva (motore interno, `android-app/`) sostituisce l'app di oggi come **aggiornamento**: stesso nome del
pacchetto (`com.buddy4free.risparmio`) e stessa chiave di caricamento. I tester la ricevono dal Play Store come una
normale nuova versione.

## 1. Compilare il pacchetto
GitHub → Actions → **App Android definitiva** → Run workflow → tipo **finale**, numero di versione **10**
(deve essere più alto dell'ultimo caricato: oggi è 2), nome **2.0.0**. In fondo alla pagina dell'esecuzione,
Artifacts → `buddy4free-risparmio-v10` (dentro c'è il file `.aab`).

## 2. Play Console, prima di caricare
L'app legge i **passi** da Connessione Salute (Health Connect): Google chiede una dichiarazione.
Play Console → Monitora e migliora (o Policy) → **Contenuti dell'app** → **Connessione Salute** (Health Connect):

- **Tipi di dati:** Passi (Steps), **solo lettura**.
- **Perché li legge (testo da incollare):**
  > L'app mostra i passi giornalieri dell'utente nella sezione Benessere, accanto ai suoi dati di risparmio, come
  > promemoria di abitudini sane. Legge solo il numero di passi degli ultimi 30 giorni, solo dopo che l'utente tocca
  > "Collega i passi del telefono" e concede il permesso. I passi restano sul telefono: non vengono inviati a server,
  > non sono usati per pubblicità né condivisi con terzi.
- **In inglese, se richiesto:**
  > The app shows the user's daily step count in its Wellbeing section, next to their savings data, as a reminder of
  > healthy habits. It reads only daily step counts for the last 30 days, only after the user taps "Connect phone
  > steps" and grants permission. Steps stay on the device: they are never sent to a server, used for advertising or
  > shared with third parties.
- **Informativa privacy:** è già aggiornata (versione 1.1, 17/11/2026, sezione 3 "Passi da Connessione Salute").

**Sicurezza dei dati (Data safety):** i passi non lasciano il telefono, quindi per Google non sono "raccolti":
la scheda resta com'è. Da ricontrollare solo se Google lo segnala.

## 3. Caricare sul test chiuso
Play Console → Test → **Test chiuso** → la traccia dei tester → **Crea nuova release** → carica il file `.aab` →
note di rilascio (sotto) → Rivedi → Avvia l'implementazione.

**Note di rilascio (it-IT):**
> Nuova app, più veloce e indipendente dal browser: notifiche all'orario che scegli, foto degli scontrini, passi da
> Samsung Health e Garmin (Connessione Salute), salvataggi in Download/Buddy4Free. Al primo avvio: "Porta qui i miei
> dati" per portare i tuoi movimenti dalla versione di prima.

## 4. Messaggio per i tester
(17/11: il backup è la via più sicura; il trasloco con Condividi resta come alternativa)
> Ciao! Sul Play Store è arrivata la nuova versione di Buddy4Free Risparmio: un'app vera, che non dipende più dal browser.
> Novità: notifiche all'orario che scegli, foto degli scontrini, i passi letti da Samsung Health o Garmin.
> **Per portare i vostri dati, 3 passi:**
> 1. **Prima di aggiornare**, aprite l'app e fate un backup: Impostazioni → Backup (il file va nella cartella Download).
> 2. Aggiornate dal Play Store e aprite l'app: parte vuota, è normale.
> 3. Accettate i termini, toccate **"Ho un file di backup"** e scegliete il file appena salvato → **Sì, ripristina**.
> Prima di confermare l'app vi mostra la data dell'ultimo movimento: controllate che sia quella giusta.
> Poi usatela come sempre e lasciate un commento dal Play Store: ci serve per l'uscita pubblica. Grazie!

## 5. Ripresentare la domanda di produzione
Dopo almeno 14 giorni dall'inizio del secondo giro e qualche giorno di uso dell'app nuova. Aggiornare le risposte in
`store/PRODUZIONE.md` con: aggiornamenti pubblicati sul test chiuso, app nuova, feedback dei tester.
