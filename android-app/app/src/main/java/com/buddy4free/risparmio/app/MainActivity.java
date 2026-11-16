package com.buddy4free.risparmio.app;

import android.app.Activity;
import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.graphics.Color;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
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
    private static final int REQ_FILE = 1, REQ_SAVE = 2;

    private WebView web;
    private ValueCallback<Uri[]> fileCb;
    private String saveId;
    private byte[] saveData;

    @Override
    protected void onCreate(Bundle state) {
        super.onCreate(state);
        FrameLayout root = new FrameLayout(this);
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
                .addPathHandler("/assets/", new WebViewAssetLoader.AssetsPathHandler(this))
                .build();
        web.setWebViewClient(new WebViewClient() {
            @Override
            public WebResourceResponse shouldInterceptRequest(WebView v, WebResourceRequest r) {
                return loader.shouldInterceptRequest(r.getUrl());
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
                try {
                    startActivityForResult(p.createIntent(), REQ_FILE);
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

        web.loadUrl(HOME);
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
            runOnUiThread(() -> {
                saveId = id;
                saveData = data;
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

        @JavascriptInterface
        public String version() {
            try {
                return getPackageManager().getPackageInfo(getPackageName(), 0).versionName;
            } catch (Exception e) {
                return "";
            }
        }
    }

    private void fatto(String id, String esito) {
        runOnUiThread(() -> web.evaluateJavascript("window.__b4fSaveDone&&window.__b4fSaveDone(" + JSONObject.quote(id == null ? "" : id) + "," + JSONObject.quote(esito) + ")", null));
    }

    @Override
    protected void onActivityResult(int req, int res, Intent data) {
        super.onActivityResult(req, res, data);
        if (req == REQ_FILE) {
            if (fileCb != null) fileCb.onReceiveValue(WebChromeClient.FileChooserParams.parseResult(res, data));
            fileCb = null;
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
    }

    @Override
    protected void onDestroy() {
        web.destroy();
        super.onDestroy();
    }
}
