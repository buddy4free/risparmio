package com.buddy4free.risparmio.app

import android.content.Context
import android.content.Intent
import androidx.health.connect.client.HealthConnectClient
import androidx.health.connect.client.PermissionController
import androidx.health.connect.client.permission.HealthPermission
import androidx.health.connect.client.records.StepsRecord
import androidx.health.connect.client.request.AggregateGroupByPeriodRequest
import androidx.health.connect.client.time.TimeRangeFilter
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import org.json.JSONObject
import java.time.LocalDate
import java.time.Period
import java.util.function.Consumer

/**
 * Passi giornalieri da Health Connect, l'archivio salute di Android dove scrivono Samsung Health, Garmin e altre app.
 * Solo lettura e solo i passi: i numeri restano sul telefono, nella memoria dell'app.
 * Health Connect somma le fonti senza doppioni (telefono e orologio insieme).
 */
object Passi {
    private val PERMESSI = setOf(HealthPermission.getReadPermission(StepsRecord::class))

    /** "ok", "aggiornare" (Health Connect da aggiornare) o "nonDisponibile". */
    @JvmStatic
    fun stato(ctx: Context): String = when (HealthConnectClient.getSdkStatus(ctx)) {
        HealthConnectClient.SDK_AVAILABLE -> "ok"
        HealthConnectClient.SDK_UNAVAILABLE_PROVIDER_UPDATE_REQUIRED -> "aggiornare"
        else -> "nonDisponibile"
    }

    /** La richiesta di permesso di Health Connect ("Passi", sola lettura). */
    @JvmStatic
    fun intentPermesso(ctx: Context): Intent =
        PermissionController.createRequestPermissionResultContract().createIntent(ctx, PERMESSI)

    /** Legge i passi degli ultimi giorni e risponde con un JSON: {stato, giorni:{"2026-11-16": 8432, …}}. */
    @JvmStatic
    fun leggi(ctx: Context, giorni: Int, fine: Consumer<String>) {
        CoroutineScope(Dispatchers.IO).launch {
            val out = JSONObject()
            try {
                val st = stato(ctx)
                if (st != "ok") {
                    out.put("stato", st)
                } else {
                    val c = HealthConnectClient.getOrCreate(ctx)
                    if (!c.permissionController.getGrantedPermissions().containsAll(PERMESSI)) {
                        out.put("stato", "permesso")
                    } else {
                        val oggi = LocalDate.now()
                        val inizio = oggi.minusDays((giorni.coerceIn(1, 60) - 1).toLong()).atStartOfDay()
                        val res = c.aggregateGroupByPeriod(
                            AggregateGroupByPeriodRequest(
                                metrics = setOf(StepsRecord.COUNT_TOTAL),
                                timeRangeFilter = TimeRangeFilter.between(inizio, oggi.plusDays(1).atStartOfDay()),
                                timeRangeSlicer = Period.ofDays(1)
                            )
                        )
                        val g = JSONObject()
                        for (r in res) {
                            val n = r.result[StepsRecord.COUNT_TOTAL]
                            if (n != null) g.put(r.startTime.toLocalDate().toString(), n)
                        }
                        out.put("stato", "ok")
                        out.put("giorni", g)
                    }
                }
            } catch (e: Exception) {
                out.put("stato", "errore")
                out.put("msg", e.toString().take(200))
            }
            fine.accept(out.toString())
        }
    }
}
