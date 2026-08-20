package com.familyforce.neonstreets;

import android.content.Context;
import android.content.SharedPreferences;
import android.os.Debug;
import android.os.SystemClock;

/**
 * Small, allocation-conscious flight recorder for diagnosing a session that
 * ends on a customer device. It deliberately stores game state only: no input
 * history, personal data, or customer images are recorded.
 */
final class RuntimeDiagnostics {
    private static final String PREFS = "family_force_runtime_diagnostics";
    private static final int EVENT_CAPACITY = 12;

    private final SharedPreferences prefs;
    private final String[] events = new String[EVENT_CAPACITY];
    private int eventCount;
    private int eventCursor;
    private final boolean previousSessionInterrupted;

    RuntimeDiagnostics(Context context) {
        prefs = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE);
        previousSessionInterrupted = prefs.getBoolean("session_active", false);
        SharedPreferences.Editor editor = prefs.edit()
                .putBoolean("session_active", true)
                .putLong("session_started_ms", SystemClock.elapsedRealtime());
        if (previousSessionInterrupted) {
            // Preserve the last complete sample before the new session starts
            // writing its own snapshots.
            editor.putString("previous_interrupted_report",
                    prefs.getString("current_report", "no prior snapshot"));
        }
        editor.apply();
        event("SESSION_START");
    }

    boolean previousSessionInterrupted() {
        return previousSessionInterrupted;
    }

    synchronized void event(String message) {
        if (message == null) return;
        events[eventCursor] = compact(message);
        eventCursor = (eventCursor + 1) % EVENT_CAPACITY;
        if (eventCount < EVENT_CAPACITY) eventCount++;
    }

    synchronized void snapshot(String state, int zone, boolean zoneActive,
                               int p1Health, int p2Health, int enemyCount,
                               int weaponType, int action, int stageFrames) {
        Runtime runtime = Runtime.getRuntime();
        long javaUsedKb = (runtime.totalMemory() - runtime.freeMemory()) / 1024L;
        long nativeKb = Debug.getNativeHeapAllocatedSize() / 1024L;
        String report = "state=" + compact(state) + ";zone=" + zone
                + ";active=" + zoneActive + ";p1=" + p1Health + ";p2=" + p2Health
                + ";enemies=" + enemyCount + ";weapon=" + weaponType + ";action=" + action
                + ";frame=" + stageFrames + ";javaKb=" + javaUsedKb + ";nativeKb=" + nativeKb;
        prefs.edit()
                .putBoolean("session_active", true)
                .putLong("snapshot_ms", SystemClock.elapsedRealtime())
                .putString("state", compact(state))
                .putInt("zone", zone)
                .putBoolean("zone_active", zoneActive)
                .putInt("p1_health", p1Health)
                .putInt("p2_health", p2Health)
                .putInt("enemy_count", enemyCount)
                .putInt("weapon", weaponType)
                .putInt("action", action)
                .putInt("stage_frames", stageFrames)
                .putLong("java_used_kb", javaUsedKb)
                .putLong("native_heap_kb", nativeKb)
                .putString("current_report", report)
                .putString("events", eventLog())
                .apply();
    }

    synchronized void failure(String phase, Throwable error) {
        String type = error == null ? "unknown" : error.getClass().getSimpleName();
        event("FAIL " + compact(phase) + " " + compact(type));
        prefs.edit()
                .putBoolean("session_active", true)
                .putString("last_failure", compact(phase) + ": " + compact(type))
                .putString("events", eventLog())
                .apply();
    }

    synchronized void closeCleanly() {
        event("SESSION_END");
        prefs.edit()
                .putBoolean("session_active", false)
                .putString("events", eventLog())
                .apply();
    }

    private String eventLog() {
        StringBuilder out = new StringBuilder(EVENT_CAPACITY * 20);
        int first = eventCount == EVENT_CAPACITY ? eventCursor : 0;
        for (int i = 0; i < eventCount; i++) {
            if (i > 0) out.append(" | ");
            String value = events[(first + i) % EVENT_CAPACITY];
            if (value != null) out.append(value);
        }
        return out.toString();
    }

    private static String compact(String text) {
        if (text == null) return "-";
        String safe = text.replace('\n', ' ').replace('\r', ' ');
        return safe.length() <= 72 ? safe : safe.substring(0, 72);
    }
}
