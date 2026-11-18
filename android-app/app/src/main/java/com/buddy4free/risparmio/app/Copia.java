package com.buddy4free.risparmio.app;

import android.content.Context;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;

/**
 * Copia dei dati dell'app in un unico file (files/copia/dati.json), l'unico incluso nel backup automatico di Android.
 * Il backup di Android è cifrato con il blocco schermo del telefono e resta nell'account Google dell'utente:
 * su un telefono nuovo, o reinstallando l'app, la pagina trova la copia e chiede se ripristinarla.
 */
final class Copia {
    private Copia() {}

    private static File file(Context c) {
        return new File(new File(c.getFilesDir(), "copia"), "dati.json");
    }

    static synchronized void salva(Context c, String json) {
        try {
            File f = file(c), dir = f.getParentFile(), tmp = new File(dir, "dati.json.tmp");
            if (!dir.isDirectory() && !dir.mkdirs()) return;
            try (OutputStream o = new FileOutputStream(tmp)) {
                o.write(json.getBytes(StandardCharsets.UTF_8));
                ((FileOutputStream) o).getFD().sync();
            }
            if (!tmp.renameTo(f)) tmp.delete();
        } catch (Exception ignored) {
        }
    }

    static synchronized String leggi(Context c) {
        File f = file(c);
        if (!f.isFile() || f.length() > 30_000_000) return "";
        try (InputStream in = new FileInputStream(f)) {
            ByteArrayOutputStream b = new ByteArrayOutputStream();
            byte[] buf = new byte[65536];
            int n;
            while ((n = in.read(buf)) > 0) b.write(buf, 0, n);
            return b.toString("UTF-8");
        } catch (Exception e) {
            return "";
        }
    }

    static synchronized void cancella(Context c) {
        file(c).delete();
    }
}
