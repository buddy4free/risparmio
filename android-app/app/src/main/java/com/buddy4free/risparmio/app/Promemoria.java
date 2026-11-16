package com.buddy4free.risparmio.app;

import android.app.AlarmManager;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Build;

import org.json.JSONArray;
import org.json.JSONObject;

import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;
import java.util.HashSet;
import java.util.Locale;
import java.util.Set;

/**
 * Promemoria dell'app: ognuno all'orario scelto nelle Impostazioni, ogni giorno o il 1° del mese.
 * Senza server: li programma il telefono. L'elenco arriva dalla pagina (setReminders) e resta salvato qui.
 * Alcuni si saltano se la cosa è già fatta oggi (spese segnate, domanda del giorno, tappa della palestra).
 */
public class Promemoria extends BroadcastReceiver {
    static final String PREF = "promemoria", AZIONE = "com.buddy4free.risparmio.PROMEMORIA", CANALE = "promemoria";

    static void salva(Context c, String json) {
        c.getSharedPreferences(PREF, Context.MODE_PRIVATE).edit().putString("dati", json).apply();
        programma(c);
    }

    private static JSONObject dati(Context c) {
        try {
            return new JSONObject(c.getSharedPreferences(PREF, Context.MODE_PRIVATE).getString("dati", "{}"));
        } catch (Exception e) {
            return new JSONObject();
        }
    }

    /** Programma il prossimo avviso di ogni promemoria attivo e cancella quelli tolti. */
    static void programma(Context c) {
        AlarmManager am = (AlarmManager) c.getSystemService(Context.ALARM_SERVICE);
        SharedPreferences sp = c.getSharedPreferences(PREF, Context.MODE_PRIVATE);
        Set<String> prima = new HashSet<>(sp.getStringSet("attivi", new HashSet<>())), ora = new HashSet<>();
        JSONObject prossimi = new JSONObject();
        JSONArray L = dati(c).optJSONArray("list");
        for (int k = 0; L != null && k < L.length(); k++) {
            JSONObject r = L.optJSONObject(k);
            if (r == null) continue;
            String id = r.optString("id");
            long t = prossimo(r.optString("at", "21:00"), r.optBoolean("m"));
            if (id.isEmpty() || t <= 0) continue;
            ora.add(id);
            // suona anche con il telefono a riposo. Puntuale al minuto se l'utente ha concesso "Sveglie e promemoria",
            // altrimenti Android può spostarlo di qualche minuto per risparmiare batteria
            if (puntuali(am)) am.setExactAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, t, pi(c, id));
            else am.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, t, pi(c, id));
            try { prossimi.put(id, t); } catch (Exception ignored) { }
        }
        for (String id : prima) if (!ora.contains(id)) am.cancel(pi(c, id));
        sp.edit().putStringSet("attivi", ora).putString("prossimi", prossimi.toString()).apply();
    }

    static boolean puntuali(AlarmManager am) {
        return Build.VERSION.SDK_INT < 31 || am.canScheduleExactAlarms();
    }

    /** Per la pagina: quando suonerà ogni promemoria (millisecondi). */
    static String prossimi(Context c) {
        return c.getSharedPreferences(PREF, Context.MODE_PRIVATE).getString("prossimi", "{}");
    }

    private static PendingIntent pi(Context c, String id) {
        Intent i = new Intent(c, Promemoria.class).setAction(AZIONE).putExtra("id", id);
        return PendingIntent.getBroadcast(c, id.hashCode(), i, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
    }

    /** Il prossimo momento in cui suonare: oggi o domani all'ora scelta, oppure il 1° del mese. */
    private static long prossimo(String hhmm, boolean mensile) {
        int h, m;
        try {
            String[] p = hhmm.split(":");
            h = Integer.parseInt(p[0]);
            m = Integer.parseInt(p[1]);
        } catch (Exception e) {
            return -1;
        }
        Calendar now = Calendar.getInstance(), t = Calendar.getInstance();
        t.set(Calendar.HOUR_OF_DAY, h);
        t.set(Calendar.MINUTE, m);
        t.set(Calendar.SECOND, 0);
        t.set(Calendar.MILLISECOND, 0);
        if (mensile) {
            t.set(Calendar.DAY_OF_MONTH, 1);
            if (!t.after(now)) t.add(Calendar.MONTH, 1);
        } else if (!t.after(now)) {
            t.add(Calendar.DAY_OF_MONTH, 1);
        }
        return t.getTimeInMillis();
    }

    static void canale(Context c) {
        if (Build.VERSION.SDK_INT < 26) return;
        NotificationManager nm = c.getSystemService(NotificationManager.class);
        if (nm.getNotificationChannel(CANALE) == null) {
            NotificationChannel ch = new NotificationChannel(CANALE, "Promemoria", NotificationManager.IMPORTANCE_DEFAULT);
            ch.setDescription("I promemoria scelti nelle Impostazioni dell'app");
            nm.createNotificationChannel(ch);
        }
    }

    static void mostra(Context c, String id, String titolo, String testo) {
        canale(c);
        Intent apri = new Intent(c, MainActivity.class).putExtra("vai", id).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_SINGLE_TOP);
        PendingIntent tap = PendingIntent.getActivity(c, id.hashCode(), apri, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
        android.app.Notification n = new android.app.Notification.Builder(c, CANALE)
                .setSmallIcon(R.drawable.ic_notifica)
                .setColor(0xFFFFC90A)
                .setContentTitle(titolo)
                .setContentText(testo)
                .setStyle(new android.app.Notification.BigTextStyle().bigText(testo))
                .setContentIntent(tap)
                .setAutoCancel(true)
                .build();
        try {
            c.getSystemService(NotificationManager.class).notify(id.hashCode(), n);
        } catch (SecurityException ignored) {
            // permesso delle notifiche non concesso: niente avviso
        }
    }

    @Override
    public void onReceive(Context c, Intent intent) {
        String id = intent.getStringExtra("id");
        if (id != null) {
            JSONObject d = dati(c), salta = d.optJSONObject("skip");
            String oggi = new SimpleDateFormat("yyyy-MM-dd", Locale.ITALY).format(new Date());
            JSONArray L = d.optJSONArray("list");
            for (int k = 0; L != null && k < L.length(); k++) {
                JSONObject r = L.optJSONObject(k);
                if (r == null || !id.equals(r.optString("id"))) continue;
                boolean fatto = salta != null && oggi.equals(salta.optString(id));
                if (!fatto) mostra(c, id, r.optString("t", "Buddy4Free Risparmio"), r.optString("d", ""));
            }
        }
        programma(c); // il prossimo giro
    }
}
