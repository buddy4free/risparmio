# App Android · come si crea una nuova versione

L'app sul Play Store è un "guscio" (Trusted Web Activity) che apre il sito
`https://buddy4free.github.io/risparmio/` a schermo intero.
Le modifiche al sito arrivano subito a tutti; un nuovo pacchetto serve solo se cambia qualcosa di Android.

## Nuova versione del pacchetto
1. GitHub → **Actions → App Android → Run workflow**.
2. `version_code`: un numero **più alto** dell'ultimo caricato (ultimo: **3**). `version_name`: es. `1.0.2`.
3. Dopo ~3 minuti, nella pagina del lavoro: **Artifacts → buddy4free-risparmio-vN-firmato** → dentro c'è `app-release.aab`.
4. Play Console → traccia → **Crea nuova release** → carica l'`.aab` → invia in revisione.

Il workflow firma con la chiave di caricamento presa dai Secrets
(`ANDROID_KEYSTORE_BASE64`, `ANDROID_KEYSTORE_PASSWORD`, `ANDROID_KEY_ALIAS`, `ANDROID_KEY_PASSWORD`)
e si ferma se l'impronta non è quella registrata sulla Play Console.

## Browser usato
`android/app/src/main/java/com/buddy4free/risparmio/LauncherActivity.java` apre l'app con **Chrome** se è installato e attivo,
altrimenti con il browser predefinito. I dati restano nel browser che apre l'app: cambiando browser servono backup e ripristino.

## Da decidere prima della pubblicazione per tutti
Soluzione definitiva per non dipendere dal browser del telefono (colori con Samsung Internet, notifiche, dati legati al browser):
valutare un pacchetto con motore interno (WebView), con migrazione dei dati tramite backup.
