package com.buddy4free.risparmio.app;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;

/** Dopo un riavvio del telefono o un aggiornamento dell'app, i promemoria si riprogrammano da soli. */
public class Avvio extends BroadcastReceiver {
    @Override
    public void onReceive(Context c, Intent intent) {
        String a = intent.getAction();
        if (Intent.ACTION_BOOT_COMPLETED.equals(a) || Intent.ACTION_MY_PACKAGE_REPLACED.equals(a)) Promemoria.programma(c);
    }
}
