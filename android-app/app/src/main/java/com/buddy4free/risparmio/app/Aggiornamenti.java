package com.buddy4free.risparmio.app;

import android.content.Context;
import android.webkit.WebResourceResponse;

import androidx.webkit.WebViewAssetLoader;

import org.json.JSONObject;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.security.KeyFactory;
import java.security.MessageDigest;
import java.security.PublicKey;
import java.security.Signature;
import java.security.spec.X509EncodedKeySpec;
import java.util.Iterator;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Aggiornamenti "ibridi": le schermate nuove arrivano dal sito, come per l'app web, ma l'app le accetta solo se
 * l'elenco dei file è firmato con la chiave di Lorenzo e ogni file scaricato ha l'impronta scritta nell'elenco.
 * Le modifiche alla parte nativa (Android) arrivano invece dal Play Store.
 */
final class Aggiornamenti {
    static final String SITO = "https://buddy4free.github.io/risparmio/";
    /** Versione delle funzioni native: una pagina che ne chiede di più nuove si ignora finché non si aggiorna l'app. */
    static final int NATIVO = 1;
    /** Chiave pubblica di Lorenzo (ECDSA P-256): solo chi ha la privata può firmare un aggiornamento. */
    private static final String CHIAVE = "MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEsF62xuj6YRLAY8ieT/IukYQ5Ll+TpKXyLYG8hqtmvTQt+WaMlSPpxJeLfD58ZT/U7ejFVdlbz47fDqYoOHCjYA==";
    private static final Pattern PERCORSO = Pattern.compile("^[A-Za-z0-9_-]+(/[A-Za-z0-9_.-]+)*\\.[A-Za-z0-9]+$");
    private static String inclusa;

    private Aggiornamenti() { }

    private static File base(Context c) {
        return new File(c.getFilesDir(), "pagina");
    }

    /** Versione della pagina inclusa nel pacchetto (dal meta b4f-build di index.html). */
    static synchronized String versioneInclusa(Context c) {
        if (inclusa != null) return inclusa;
        inclusa = "0";
        try (InputStream in = c.getAssets().open("www/index.html")) {
            byte[] b = new byte[4096];
            int n = in.read(b);
            Matcher m = Pattern.compile("name=\"b4f-build\" content=\"(\\d+)\"").matcher(new String(b, 0, Math.max(0, n), StandardCharsets.UTF_8));
            if (m.find()) inclusa = m.group(1);
        } catch (Exception ignored) { }
        return inclusa;
    }

    /** Versione scaricata in uso, solo se più nuova di quella inclusa nel pacchetto. */
    static String versioneScaricata(Context c) {
        try {
            String v = leggiTesto(new File(base(c), "attiva.txt")).trim();
            if (v.matches("\\d{6,}") && v.compareTo(versioneInclusa(c)) > 0 && new File(base(c), v).isDirectory()) return v;
        } catch (Exception ignored) { }
        return null;
    }

    static String versioneInUso(Context c) {
        String v = versioneScaricata(c);
        return v != null ? v : versioneInclusa(c);
    }

    /** I file della pagina: prima quelli scaricati e verificati, altrimenti quelli inclusi nel pacchetto. */
    static final class Pagina implements WebViewAssetLoader.PathHandler {
        private final Context c;
        private final WebViewAssetLoader.AssetsPathHandler inclusi;

        Pagina(Context c) {
            this.c = c.getApplicationContext();
            this.inclusi = new WebViewAssetLoader.AssetsPathHandler(c);
        }

        @Override
        public WebResourceResponse handle(String path) {
            if (path.startsWith("www/")) {
                String v = versioneScaricata(c);
                if (v != null) {
                    File f = new File(new File(base(c), v), path.substring(4));
                    if (f.isFile()) {
                        try {
                            return new WebResourceResponse(tipo(path), null, new FileInputStream(f));
                        } catch (Exception ignored) { }
                    }
                }
            }
            return inclusi.handle(path);
        }
    }

    private static String tipo(String p) {
        String e = p.substring(p.lastIndexOf('.') + 1).toLowerCase();
        switch (e) {
            case "html": return "text/html";
            case "js": return "text/javascript";
            case "css": return "text/css";
            case "json": case "webmanifest": return "application/json";
            case "png": return "image/png";
            case "webp": return "image/webp";
            case "svg": return "image/svg+xml";
            case "woff2": return "font/woff2";
            case "wasm": return "application/wasm";
            default: return "application/octet-stream";
        }
    }

    /**
     * Controlla il sito: se c'è una versione più nuova, firmata e compatibile, la scarica, verifica ogni file
     * e la attiva per la prossima apertura della pagina. Restituisce true se ne ha installata una nuova.
     */
    static synchronized boolean controlla(Context c) {
        try {
            byte[] elenco = scarica(SITO + "app/aggiornamento.json?t=" + System.currentTimeMillis(), 256 * 1024);
            byte[] firma = android.util.Base64.decode(new String(scarica(SITO + "app/aggiornamento.sig?t=" + System.currentTimeMillis(), 4096), StandardCharsets.US_ASCII).trim(), android.util.Base64.DEFAULT);
            PublicKey k = KeyFactory.getInstance("EC").generatePublic(new X509EncodedKeySpec(android.util.Base64.decode(CHIAVE, android.util.Base64.DEFAULT)));
            Signature s = Signature.getInstance("SHA256withECDSA");
            s.initVerify(k);
            s.update(elenco);
            if (!s.verify(firma)) return false; // non firmato da Lorenzo: si ignora

            JSONObject j = new JSONObject(new String(elenco, StandardCharsets.UTF_8));
            String ver = j.getString("ver");
            if (!ver.matches("\\d{6,}") || ver.compareTo(versioneInUso(c)) <= 0) return false; // niente di nuovo (o più vecchio)
            if (j.optInt("nativo", 1) > NATIVO) return false; // serve un'app più nuova dal Play Store

            File dir = new File(base(c), ver), tmp = new File(base(c), ver + ".tmp");
            cancella(tmp);
            JSONObject files = j.getJSONObject("files");
            for (Iterator<String> it = files.keys(); it.hasNext(); ) {
                String p = it.next(), atteso = files.getString(p);
                if (!PERCORSO.matcher(p).matches() || p.contains("..")) { cancella(tmp); return false; }
                byte[] d = scarica(SITO + p + "?v=" + ver, 30 * 1024 * 1024);
                if (!hex(MessageDigest.getInstance("SHA-256").digest(d)).equals(atteso)) { cancella(tmp); return false; } // file diverso da quello firmato
                File f = new File(tmp, p);
                File parent = f.getParentFile();
                if (parent != null && !parent.isDirectory() && !parent.mkdirs()) throw new java.io.IOException("cartella");
                try (FileOutputStream o = new FileOutputStream(f)) { o.write(d); }
            }
            cancella(dir);
            if (!tmp.renameTo(dir)) { cancella(tmp); return false; }
            File a = new File(base(c), "attiva.txt.tmp");
            try (FileOutputStream o = new FileOutputStream(a)) { o.write(ver.getBytes(StandardCharsets.US_ASCII)); }
            if (!a.renameTo(new File(base(c), "attiva.txt"))) return false;
            // si tengono solo la versione nuova e quella di prima
            File[] tutte = base(c).listFiles();
            if (tutte != null) for (File x : tutte) if (x.isDirectory() && !x.getName().equals(ver) && x.getName().compareTo(ver) < 0 && !x.getName().equals(versionePrecedente(tutte, ver))) cancella(x);
            return true;
        } catch (Exception e) {
            return false; // niente rete o sito irraggiungibile: si riprova più tardi
        }
    }

    private static String versionePrecedente(File[] tutte, String ver) {
        String best = "";
        for (File x : tutte) if (x.isDirectory() && x.getName().matches("\\d{6,}") && x.getName().compareTo(ver) < 0 && x.getName().compareTo(best) > 0) best = x.getName();
        return best;
    }

    private static byte[] scarica(String url, int max) throws Exception {
        HttpURLConnection h = (HttpURLConnection) new URL(url).openConnection();
        h.setConnectTimeout(15000);
        h.setReadTimeout(30000);
        h.setUseCaches(false);
        h.setInstanceFollowRedirects(true);
        try {
            if (h.getResponseCode() != 200) throw new java.io.IOException("HTTP " + h.getResponseCode());
            try (InputStream in = h.getInputStream()) {
                ByteArrayOutputStream b = new ByteArrayOutputStream();
                byte[] buf = new byte[65536];
                int n;
                while ((n = in.read(buf)) > 0) {
                    b.write(buf, 0, n);
                    if (b.size() > max) throw new java.io.IOException("troppo grande");
                }
                return b.toByteArray();
            }
        } finally {
            h.disconnect();
        }
    }

    private static String leggiTesto(File f) throws Exception {
        try (FileInputStream in = new FileInputStream(f)) {
            byte[] b = new byte[64];
            int n = in.read(b);
            return new String(b, 0, Math.max(0, n), StandardCharsets.US_ASCII);
        }
    }

    private static String hex(byte[] b) {
        StringBuilder s = new StringBuilder();
        for (byte x : b) s.append(String.format("%02x", x));
        return s.toString();
    }

    private static void cancella(File f) {
        if (!f.exists()) return;
        File[] l = f.listFiles();
        if (l != null) for (File x : l) cancella(x);
        //noinspection ResultOfMethodCallIgnored
        f.delete();
    }
}
