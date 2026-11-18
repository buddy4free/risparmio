package com.buddy4free.risparmio.app;

import android.app.Activity;
import android.content.ActivityNotFoundException;
import android.content.ContentValues;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.view.View;
import android.view.WindowInsetsController;
import androidx.core.content.FileProvider;
import java.io.File;
import android.graphics.Color;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Environment;
import android.provider.DocumentsContract;
import android.provider.MediaStore;
import android.util.Base64;
import android.view.WindowInsets;
import android.webkit.JavascriptInterface;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.FrameLayout;
import android.widget.Toast;
import android.window.OnBackInvokedDispatcher;

import androidx.webkit.WebViewAssetLoader;

import org.json.JSONObject;

import java.io.OutputStream;

/**
 * Buddy4Free Risparmio, app definitiva: la stessa pagina dell'app web, inclusa nel pacchetto
 * e aperta con il motore interno di Android (WebView). Niente Chrome, niente rete:
 * i dati restano nella memoria dell'app, sul telefono.
 */
public class MainActivity extends Activity {
    private static final String HOST = "appassets.androidplatform.net";
    private static final String HOME = "https://" + HOST + "/assets/www/index.html";
    private static final int REQ_FILE = 1, REQ_SAVE = 2, REQ_NOTIF = 3, REQ_PASSI = 4;
    private static final String CARTELLA = "Buddy4Free";

    private WebView web;
    private ValueCallback<Uri[]> fileCb;
    private String saveId;
    private byte[] saveData;
    private String saveMime;
    private Uri ultimoFile;       // l'ultimo file salvato (PDF, CSV, immagine): si può aprire o condividere subito
    private String ultimoMime;
    private Uri fotoUri;          // foto dello scontrino appena scattata
    private String vaiA;          // schermata da aprire toccando una notifica
    private String daImportare;   // dati arrivati con Condividi (trasloco)
    private boolean pronta;       // la pagina ha finito di caricarsi
    private FrameLayout root;

    @Override
    protected void onCreate(Bundle state) {
        super.onCreate(state);
        root = new FrameLayout(this);
        root.setBackgroundColor(Color.BLACK);
        web = new WebView(this);
        web.setBackgroundColor(Color.BLACK);
        root.addView(web, new FrameLayout.LayoutParams(FrameLayout.LayoutParams.MATCH_PARENT, FrameLayout.LayoutParams.MATCH_PARENT));
        setContentView(root);

        // la pagina sta tra la barra di stato e quella di navigazione (e sopra la tastiera quando è aperta)
        root.setOnApplyWindowInsetsListener((v, ins) -> {
            if (Build.VERSION.SDK_INT >= 30) {
                android.graphics.Insets i = ins.getInsets(WindowInsets.Type.systemBars() | WindowInsets.Type.ime() | WindowInsets.Type.displayCutout());
                v.setPadding(i.left, i.top, i.right, i.bottom);
                return WindowInsets.CONSUMED;
            }
            v.setPadding(ins.getSystemWindowInsetLeft(), ins.getSystemWindowInsetTop(), ins.getSystemWindowInsetRight(), ins.getSystemWindowInsetBottom());
            return ins.consumeSystemWindowInsets();
        });

        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setDatabaseEnabled(true);
        s.setAllowFileAccess(false);
        s.setAllowContentAccess(false);
        s.setSupportMultipleWindows(false);
        s.setTextZoom(100);
        s.setMediaPlaybackRequiresUserGesture(false);

        // i file della pagina arrivano dal pacchetto, con un indirizzo https sicuro
        final WebViewAssetLoader loader = new WebViewAssetLoader.Builder()
                .addPathHandler("/assets/", new Aggiornamenti.Pagina(this)) // prima le schermate aggiornate e verificate, poi quelle incluse
                .build();
        web.setWebViewClient(new WebViewClient() {
            @Override
            public WebResourceResponse shouldInterceptRequest(WebView v, WebResourceRequest r) {
                return loader.shouldInterceptRequest(r.getUrl());
            }

            @Override
            public void onPageFinished(WebView v, String url) {
                pronta = true;
                apriSchermata();
            }

            @Override
            public boolean shouldOverrideUrlLoading(WebView v, WebResourceRequest r) {
                Uri u = r.getUrl();
                if (HOST.equals(u.getHost())) return false;
                apriFuori(u); // sito, mail, calendario: nelle altre app del telefono
                return true;
            }
        });
        web.setWebChromeClient(new WebChromeClient() {
            @Override
            public boolean onShowFileChooser(WebView v, ValueCallback<Uri[]> cb, FileChooserParams p) {
                if (fileCb != null) fileCb.onReceiveValue(null);
                fileCb = cb;
                fotoUri = null;
                String[] tipi = p.getAcceptTypes();
                boolean immagine = tipi != null && tipi.length > 0 && tipi[0] != null && tipi[0].startsWith("image");
                if (immagine) { // scontrino: si sceglie tra fotocamera e galleria
                    Intent galleria = new Intent(Intent.ACTION_GET_CONTENT).setType("image/*").addCategory(Intent.CATEGORY_OPENABLE);
                    Intent scelta = Intent.createChooser(galleria, "Foto dello scontrino");
                    try {
                        File dir = new File(getCacheDir(), "foto");
                        dir.mkdirs();
                        fotoUri = FileProvider.getUriForFile(MainActivity.this, getPackageName() + ".foto", new File(dir, "scontrino.jpg"));
                        Intent cam = new Intent(MediaStore.ACTION_IMAGE_CAPTURE).putExtra(MediaStore.EXTRA_OUTPUT, fotoUri)
                                .addFlags(Intent.FLAG_GRANT_WRITE_URI_PERMISSION | Intent.FLAG_GRANT_READ_URI_PERMISSION);
                        scelta.putExtra(Intent.EXTRA_INITIAL_INTENTS, new Intent[]{cam});
                    } catch (Exception e) {
                        fotoUri = null;
                    }
                    try {
                        startActivityForResult(scelta, REQ_FILE);
                    } catch (ActivityNotFoundException e) {
                        fileCb = null;
                        return false;
                    }
                    return true;
                }
                Intent i = new Intent(Intent.ACTION_OPEN_DOCUMENT);
                i.addCategory(Intent.CATEGORY_OPENABLE);
                i.setType("*/*"); // i backup salvati da altre app non sempre risultano "json": si sceglie tra tutti i file
                if (Build.VERSION.SDK_INT >= 26) i.putExtra(DocumentsContract.EXTRA_INITIAL_URI, DocumentsContract.buildDocumentUri("com.android.externalstorage.documents", "primary:" + Environment.DIRECTORY_DOWNLOADS + "/" + CARTELLA));
                try {
                    startActivityForResult(i, REQ_FILE);
                } catch (ActivityNotFoundException e) {
                    fileCb = null;
                    return false;
                }
                return true;
            }
        });
        web.addJavascriptInterface(new Ponte(), "B4FNative");

        // indietro: torna alla schermata precedente dell'app; dalla prima, l'app va in secondo piano
        if (Build.VERSION.SDK_INT >= 33) {
            getOnBackInvokedDispatcher().registerOnBackInvokedCallback(OnBackInvokedDispatcher.PRIORITY_DEFAULT, this::indietro);
        }

        vaiA = getIntent().getStringExtra("vai");
        if (perInformativa(getIntent())) vaiA = "privacy";
        daImportare = leggiCondiviso(getIntent());
        Promemoria.canale(this);
        web.loadUrl(HOME);
        controllaAggiornamenti(true);
    }

    /** Aggiornamenti firmati della pagina: all'apertura e, tornando nell'app, al massimo ogni 3 ore. */
    private void controllaAggiornamenti(boolean subito) {
        android.content.SharedPreferences sp = getSharedPreferences("aggiornamenti", MODE_PRIVATE);
        long ora = System.currentTimeMillis();
        if (!subito && ora - sp.getLong("ultimo", 0) < 3 * 3600_000L) return;
        sp.edit().putLong("ultimo", ora).apply();
        final android.content.Context c = getApplicationContext();
        new Thread(() -> {
            if (Aggiornamenti.controlla(c)) runOnUiThread(() -> { if (pronta) web.evaluateJavascript("window.__b4fUpd&&window.__b4fUpd()", null); });
        }, "aggiornamenti").start();
    }

    @Override
    protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent);
        String imp = leggiCondiviso(intent);
        if (imp != null) {
            daImportare = imp;
            apriSchermata();
            return;
        }
        String v = perInformativa(intent) ? "privacy" : intent.getStringExtra("vai");
        if (v != null) {
            vaiA = v;
            apriSchermata();
        }
    }

    /** Testo dei dati condivisi da un'altra app (file o testo), al massimo 30 MB. */
    private String leggiCondiviso(Intent i) {
        if (i == null || !Intent.ACTION_SEND.equals(i.getAction())) return null;
        try {
            Uri u = i.getParcelableExtra(Intent.EXTRA_STREAM);
            if (u != null) {
                try (java.io.InputStream in = getContentResolver().openInputStream(u)) {
                    if (in == null) return null;
                    java.io.ByteArrayOutputStream b = new java.io.ByteArrayOutputStream();
                    byte[] buf = new byte[65536];
                    int n;
                    while ((n = in.read(buf)) > 0) {
                        b.write(buf, 0, n);
                        if (b.size() > 30_000_000) return null;
                    }
                    return b.toString("UTF-8");
                }
            }
            CharSequence t = i.getCharSequenceExtra(Intent.EXTRA_TEXT);
            return t == null ? null : t.toString();
        } catch (Exception e) {
            Toast.makeText(this, "Non riesco a leggere i dati ricevuti", Toast.LENGTH_LONG).show();
            return null;
        }
    }

    private static boolean perInformativa(Intent i) {
        String a = i == null ? null : i.getAction();
        return "androidx.health.ACTION_SHOW_PERMISSIONS_RATIONALE".equals(a) || "android.intent.action.VIEW_PERMISSION_USAGE".equals(a);
    }

    /** Passi da Health Connect: la risposta torna alla pagina. Con chiedi=true, se manca il permesso lo si chiede. */
    private void passi(boolean chiedi) {
        Passi.leggi(getApplicationContext(), 30, json -> runOnUiThread(() -> {
            if (chiedi && json.contains("\"permesso\"")) {
                // Android 14 e successivi: il permesso "Passi" si chiede con la finestra dei permessi di sistema
                if (Build.VERSION.SDK_INT >= 34) {
                    requestPermissions(new String[]{"android.permission.health.READ_STEPS"}, REQ_PASSI);
                    return;
                }
                try {
                    startActivityForResult(Passi.intentPermesso(this), REQ_PASSI);
                    return;
                } catch (Exception ignored) { }
            }
            web.evaluateJavascript("window.__b4fSteps&&window.__b4fSteps(" + json + ")", null);
        }));
    }

    /** Toccando un promemoria si apre la schermata giusta (domanda del giorno, palestra, revisione…). */
    private void apriSchermata() {
        if (pronta && daImportare != null) {
            String t = daImportare;
            daImportare = null;
            web.evaluateJavascript("window.__b4fImport&&window.__b4fImport(" + JSONObject.quote(t) + ")", null);
        }
        if (!pronta || vaiA == null) return;
        String v = vaiA;
        vaiA = null;
        web.evaluateJavascript("window.__b4fGo&&window.__b4fGo(" + JSONObject.quote(v) + ")", null);
    }

    /** Barre di sistema dello stesso colore dell'app, con icone chiare o scure secondo il tema. */
    private void barre(boolean chiaro) {
        root.setBackgroundColor(chiaro ? 0xFFF5F4EF : Color.BLACK);
        web.setBackgroundColor(chiaro ? 0xFFF5F4EF : Color.BLACK);
        if (Build.VERSION.SDK_INT >= 30) {
            WindowInsetsController c = getWindow().getInsetsController();
            if (c != null) {
                int m = WindowInsetsController.APPEARANCE_LIGHT_STATUS_BARS | WindowInsetsController.APPEARANCE_LIGHT_NAVIGATION_BARS;
                c.setSystemBarsAppearance(chiaro ? m : 0, m);
            }
        } else {
            View d = getWindow().getDecorView();
            int f = d.getSystemUiVisibility(), m = View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR | View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR;
            d.setSystemUiVisibility(chiaro ? f | m : f & ~m);
        }
        if (Build.VERSION.SDK_INT < 35) {
            getWindow().setStatusBarColor(chiaro ? 0xFFF5F4EF : Color.BLACK);
            getWindow().setNavigationBarColor(chiaro ? 0xFFF5F4EF : Color.BLACK);
        }
    }

    private String permessoNotifiche() {
        if (Build.VERSION.SDK_INT < 33) return "granted";
        if (checkSelfPermission(android.Manifest.permission.POST_NOTIFICATIONS) == PackageManager.PERMISSION_GRANTED) return "granted";
        return getSharedPreferences(Promemoria.PREF, MODE_PRIVATE).getBoolean("chiesto", false) && !shouldShowRequestPermissionRationale(android.Manifest.permission.POST_NOTIFICATIONS) ? "denied" : "default";
    }

    @Override
    public void onRequestPermissionsResult(int req, String[] perm, int[] res) {
        super.onRequestPermissionsResult(req, perm, res);
        if (req == REQ_PASSI) {
            passi(false);
            return;
        }
        if (req == REQ_NOTIF) web.evaluateJavascript("window.__b4fNotifPerm&&window.__b4fNotifPerm(" + JSONObject.quote(permessoNotifiche()) + ")", null);
    }

    private void indietro() {
        if (web.canGoBack()) web.goBack();
        else moveTaskToBack(true);
    }

    @Override
    @SuppressWarnings("deprecation")
    public void onBackPressed() {
        indietro();
    }

    private void apriFuori(Uri u) {
        try {
            Intent i = "mailto".equals(u.getScheme()) ? new Intent(Intent.ACTION_SENDTO, u) : new Intent(Intent.ACTION_VIEW, u);
            i.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            startActivity(i);
        } catch (ActivityNotFoundException e) {
            Toast.makeText(this, "Nessuna app per aprire il link", Toast.LENGTH_SHORT).show();
        }
    }

    /** Collegamento con la pagina: salvataggio di backup, PDF e CSV in un file scelto dall'utente. */
    private class Ponte {
        @JavascriptInterface
        public void saveFile(String id, String name, String mime, String b64) {
            final byte[] data;
            try {
                data = Base64.decode(b64, Base64.DEFAULT);
            } catch (IllegalArgumentException e) {
                fatto(id, "err");
                return;
            }
            if (Build.VERSION.SDK_INT >= 29) {
                runOnUiThread(() -> fatto(id, salvaInDownload(name, mime, data) ? "ok" : "err"));
                return;
            }
            runOnUiThread(() -> {
                saveId = id;
                saveData = data;
                saveMime = mime;
                Intent i = new Intent(Intent.ACTION_CREATE_DOCUMENT);
                i.addCategory(Intent.CATEGORY_OPENABLE);
                i.setType(mime == null || mime.isEmpty() ? "application/octet-stream" : mime);
                i.putExtra(Intent.EXTRA_TITLE, name);
                try {
                    startActivityForResult(i, REQ_SAVE);
                } catch (ActivityNotFoundException e) {
                    saveId = null;
                    saveData = null;
                    fatto(id, "err");
                }
            });
        }

        /** Copia di un file (il backup) verso un'altra app scelta dall'utente: Google Drive, mail, WhatsApp… */
        @JavascriptInterface
        public void shareFile(String name, String mime, String b64) {
            final byte[] data;
            try {
                data = Base64.decode(b64, Base64.DEFAULT);
            } catch (IllegalArgumentException e) {
                return;
            }
            final String nome = name == null ? "buddy4free.json" : name.replaceAll("[^A-Za-z0-9._-]", "_");
            runOnUiThread(() -> {
                try {
                    File dir = new File(getCacheDir(), "condivisi");
                    File[] vecchi = dir.listFiles();
                    if (vecchi != null) for (File v : vecchi) v.delete();
                    if (!dir.isDirectory() && !dir.mkdirs()) throw new java.io.IOException("cartella");
                    File f = new File(dir, nome);
                    try (OutputStream o = new java.io.FileOutputStream(f)) { o.write(data); }
                    Uri u = FileProvider.getUriForFile(MainActivity.this, getPackageName() + ".foto", f);
                    Intent i = new Intent(Intent.ACTION_SEND)
                            .setType(mime == null || mime.isEmpty() ? "application/octet-stream" : mime)
                            .putExtra(Intent.EXTRA_STREAM, u)
                            .putExtra(Intent.EXTRA_TITLE, nome)
                            .addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
                    startActivity(Intent.createChooser(i, "Salva il backup in…"));
                } catch (Exception e) {
                    Toast.makeText(MainActivity.this, "Non riesco a condividere il file", Toast.LENGTH_SHORT).show();
                }
            });
        }

        /** Copia dei dati per il backup automatico di Android (cifrato, nell'account Google dell'utente). */
        @JavascriptInterface
        public void copiaSalva(String json) {
            if (json == null || json.length() > 30_000_000) return;
            new Thread(() -> Copia.salva(getApplicationContext(), json)).start();
        }

        /** La copia ritrovata dopo un ripristino del telefono (vuota se non c'è). */
        @JavascriptInterface
        public String copiaLeggi() {
            return Copia.leggi(getApplicationContext());
        }

        @JavascriptInterface
        public void copiaCancella() {
            Copia.cancella(getApplicationContext());
        }

        /** Apre l'ultimo file salvato (PDF, CSV, immagine) con un'app del telefono; se nessuna lo apre, si condivide. */
        @JavascriptInterface
        public void openSaved() {
            runOnUiThread(() -> {
                if (ultimoFile == null) return;
                String m = ultimoMime == null || ultimoMime.isEmpty() ? "application/octet-stream" : ultimoMime;
                Intent i = new Intent(Intent.ACTION_VIEW).setDataAndType(ultimoFile, m).addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
                try {
                    startActivity(Intent.createChooser(i, "Apri con…"));
                } catch (ActivityNotFoundException e) {
                    condividiUltimo();
                }
            });
        }

        /** Manda l'ultimo file salvato a un'altra app (WhatsApp, mail, Drive…). */
        @JavascriptInterface
        public void shareSaved() {
            runOnUiThread(MainActivity.this::condividiUltimo);
        }

        @JavascriptInterface
        public void setBars(boolean chiaro) {
            runOnUiThread(() -> barre(chiaro));
        }

        /** Elenco dei promemoria attivi, con orari, e cosa risulta già fatto oggi. */
        @JavascriptInterface
        public void setReminders(String json) {
            Promemoria.salva(getApplicationContext(), json);
        }

        @JavascriptInterface
        public String stepsStatus() {
            return Passi.stato(getApplicationContext());
        }

        /** Collega i passi: chiede il permesso di Health Connect se serve, poi legge gli ultimi 30 giorni. */
        @JavascriptInterface
        public void stepsConnect() {
            passi(true);
        }

        /** Rilegge i passi senza chiedere nulla (all'apertura di Benessere). */
        @JavascriptInterface
        public void stepsRead() {
            passi(false);
        }

        /** Per "Segnala un problema": cosa vede il telefono del collegamento con Connessione Salute. */
        @JavascriptInterface
        public String stepsDiag() {
            StringBuilder d = new StringBuilder();
            try {
                d.append("stato ").append(Passi.stato(getApplicationContext()));
                d.append(" · Android ").append(Build.VERSION.SDK_INT);
                boolean dich = false;
                String[] req = getPackageManager().getPackageInfo(getPackageName(), PackageManager.GET_PERMISSIONS).requestedPermissions;
                if (req != null) for (String r : req) if ("android.permission.health.READ_STEPS".equals(r)) dich = true;
                d.append(" · permesso dichiarato ").append(dich ? "sì" : "no");
                if (Build.VERSION.SDK_INT >= 34) d.append(" · concesso ").append(checkSelfPermission("android.permission.health.READ_STEPS") == PackageManager.PERMISSION_GRANTED ? "sì" : "no");
                Intent v = new Intent("android.intent.action.VIEW_PERMISSION_USAGE").addCategory("android.intent.category.HEALTH_PERMISSIONS").setPackage(getPackageName());
                d.append(" · informativa ").append(getPackageManager().queryIntentActivities(v, 0).isEmpty() ? "non trovata" : "trovata");
                Intent r2 = new Intent("androidx.health.ACTION_SHOW_PERMISSIONS_RATIONALE").setPackage(getPackageName());
                d.append("/").append(getPackageManager().queryIntentActivities(r2, 0).isEmpty() ? "no" : "sì");
            } catch (Exception e) {
                d.append(" · errore ").append(e.getClass().getSimpleName());
            }
            return d.toString();
        }

        /** Le autorizzazioni di Connessione Salute per questa app (lì si attiva "Passi" a mano). */
        @JavascriptInterface
        public void stepsSettings() {
            runOnUiThread(() -> {
                Intent[] prove = {
                        new Intent("android.health.connect.action.MANAGE_HEALTH_PERMISSIONS").putExtra(Intent.EXTRA_PACKAGE_NAME, getPackageName()),
                        new Intent("android.health.connect.action.HEALTH_HOME_SETTINGS"),
                        new Intent("androidx.health.ACTION_HEALTH_CONNECT_SETTINGS")
                };
                for (Intent i : prove) {
                    try {
                        startActivity(i);
                        return;
                    } catch (Exception ignored) { }
                }
                Toast.makeText(MainActivity.this, "Impostazioni → Connessione Salute → Autorizzazioni app", Toast.LENGTH_LONG).show();
            });
        }

        /** Health Connect da installare o aggiornare: la sua pagina nel Play Store. */
        @JavascriptInterface
        public void stepsInstall() {
            runOnUiThread(() -> apriFuori(Uri.parse("https://play.google.com/store/apps/details?id=com.google.android.apps.healthdata")));
        }

        @JavascriptInterface
        public boolean exactAllowed() {
            return Promemoria.puntuali((android.app.AlarmManager) getSystemService(ALARM_SERVICE));
        }

        /** Apre "Sveglie e promemoria" nelle impostazioni del telefono, per gli avvisi puntuali. */
        @JavascriptInterface
        public void askExact() {
            runOnUiThread(() -> {
                if (Build.VERSION.SDK_INT < 31) return;
                try {
                    startActivity(new Intent(android.provider.Settings.ACTION_REQUEST_SCHEDULE_EXACT_ALARM, Uri.parse("package:" + getPackageName())));
                } catch (Exception e) {
                    Toast.makeText(MainActivity.this, "Impostazioni → App → Risparmio → Sveglie e promemoria", Toast.LENGTH_LONG).show();
                }
            });
        }

        @JavascriptInterface
        public String nextReminders() {
            return Promemoria.prossimi(getApplicationContext());
        }

        @JavascriptInterface
        public String notifPermission() {
            return permessoNotifiche();
        }

        @JavascriptInterface
        public void askNotif() {
            runOnUiThread(() -> {
                if (Build.VERSION.SDK_INT >= 33 && !"granted".equals(permessoNotifiche())) {
                    getSharedPreferences(Promemoria.PREF, MODE_PRIVATE).edit().putBoolean("chiesto", true).apply();
                    requestPermissions(new String[]{android.Manifest.permission.POST_NOTIFICATIONS}, REQ_NOTIF);
                } else {
                    web.evaluateJavascript("window.__b4fNotifPerm&&window.__b4fNotifPerm(" + JSONObject.quote(permessoNotifiche()) + ")", null);
                }
            });
        }

        @JavascriptInterface
        public void testNotification() {
            Promemoria.mostra(getApplicationContext(), "prova", "Buddy4Free Risparmio", "Così arriveranno i promemoria che hai scelto.");
        }

        /** Le impostazioni delle notifiche dell'app nel telefono, per sbloccarle. */
        @JavascriptInterface
        public void openNotifSettings() {
            runOnUiThread(() -> {
                try {
                    startActivity(new Intent(android.provider.Settings.ACTION_APP_NOTIFICATION_SETTINGS).putExtra(android.provider.Settings.EXTRA_APP_PACKAGE, getPackageName()));
                } catch (Exception e) {
                    Toast.makeText(MainActivity.this, "Apri Impostazioni → App → Risparmio → Notifiche", Toast.LENGTH_LONG).show();
                }
            });
        }

        @JavascriptInterface
        public String version() {
            try {
                return getPackageManager().getPackageInfo(getPackageName(), 0).versionName;
            } catch (Exception e) {
                return "";
            }
        }
    }

    /** Scrive il file in Download/Buddy4Free, senza chiedere la cartella. Se il nome esiste già, Android aggiunge un numero. */
    private boolean salvaInDownload(String name, String mime, byte[] data) {
        ContentValues v = new ContentValues();
        v.put(MediaStore.MediaColumns.DISPLAY_NAME, name);
        v.put(MediaStore.MediaColumns.MIME_TYPE, mime == null || mime.isEmpty() ? "application/octet-stream" : mime);
        v.put(MediaStore.MediaColumns.RELATIVE_PATH, Environment.DIRECTORY_DOWNLOADS + "/" + CARTELLA);
        v.put(MediaStore.MediaColumns.IS_PENDING, 1);
        Uri u = null;
        try {
            u = getContentResolver().insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, v);
            if (u == null) return false;
            try (OutputStream o = getContentResolver().openOutputStream(u, "w")) {
                if (o == null) throw new java.io.IOException("nessun file");
                o.write(data);
            }
            v.clear();
            v.put(MediaStore.MediaColumns.IS_PENDING, 0);
            getContentResolver().update(u, v, null, null);
            Toast.makeText(this, "Salvato in Download/" + CARTELLA, Toast.LENGTH_LONG).show();
            ultimoFile = u;
            ultimoMime = mime;
            return true;
        } catch (Exception e) {
            if (u != null) try { getContentResolver().delete(u, null, null); } catch (Exception ignored) { }
            return false;
        }
    }

    private void condividiUltimo() {
        if (ultimoFile == null) return;
        Intent i = new Intent(Intent.ACTION_SEND)
                .setType(ultimoMime == null || ultimoMime.isEmpty() ? "application/octet-stream" : ultimoMime)
                .putExtra(Intent.EXTRA_STREAM, ultimoFile)
                .addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
        try {
            startActivity(Intent.createChooser(i, "Condividi con…"));
        } catch (ActivityNotFoundException e) {
            Toast.makeText(this, "Nessuna app per questo file", Toast.LENGTH_SHORT).show();
        }
    }

    private void fatto(String id, String esito) {
        runOnUiThread(() -> web.evaluateJavascript("window.__b4fSaveDone&&window.__b4fSaveDone(" + JSONObject.quote(id == null ? "" : id) + "," + JSONObject.quote(esito) + ")", null));
    }

    @Override
    protected void onActivityResult(int req, int res, Intent data) {
        super.onActivityResult(req, res, data);
        if (req == REQ_PASSI) {
            passi(false); // dopo la scelta dell'utente: si legge (o si risponde "permesso" se non concesso)
            return;
        }
        if (req == REQ_FILE) {
            Uri[] r = WebChromeClient.FileChooserParams.parseResult(res, data);
            if (res == RESULT_OK && (r == null || r.length == 0) && fotoUri != null) r = new Uri[]{fotoUri}; // foto scattata con la fotocamera
            if (fileCb != null) fileCb.onReceiveValue(r);
            fileCb = null;
            fotoUri = null;
        } else if (req == REQ_SAVE) {
            String id = saveId;
            byte[] d = saveData;
            saveId = null;
            saveData = null;
            if (res != RESULT_OK || data == null || data.getData() == null || d == null) {
                fatto(id, "declined");
                return;
            }
            try (OutputStream o = getContentResolver().openOutputStream(data.getData(), "wt")) {
                if (o == null) throw new java.io.IOException("nessun file");
                o.write(d);
                ultimoFile = data.getData();
                ultimoMime = saveMime;
                fatto(id, "ok");
            } catch (Exception e) {
                fatto(id, "err");
            }
        }
    }

    @Override
    protected void onPause() {
        // prima di andare in secondo piano la pagina scrive subito i dati in memoria
        web.evaluateJavascript("typeof saveNow==='function'&&saveNow()", null);
        web.onPause();
        super.onPause();
    }

    @Override
    protected void onResume() {
        super.onResume();
        web.onResume();
        Promemoria.programma(getApplicationContext());
        controllaAggiornamenti(false);
        if (pronta) web.evaluateJavascript("window.__b4fResume&&window.__b4fResume()", null);
    }

    @Override
    protected void onDestroy() {
        web.destroy();
        super.onDestroy();
    }
}
