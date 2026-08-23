package com.familyforce.neonstreets;

import android.content.SharedPreferences;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

/** Allocation-light local top-ten table; no account, permission, or network required. */
final class ArcadeLeaderboard {
    private static final String KEY = "arcade_top_scores";

    private ArcadeLeaderboard() {}

    static int[] load(SharedPreferences prefs) {
        ArrayList<Integer> values = new ArrayList<>();
        String saved = prefs.getString(KEY, "");
        if (saved != null && !saved.isEmpty()) {
            for (String token : saved.split(",")) {
                try {
                    values.add(Math.max(0, Integer.parseInt(token)));
                } catch (NumberFormatException ignored) {
                    // Preserve the remaining valid scores after a damaged preference.
                }
            }
        }
        Collections.sort(values, Collections.reverseOrder());
        int[] result = new int[Math.min(10, values.size())];
        for (int index = 0; index < result.length; index++) result[index] = values.get(index);
        return result;
    }

    static int[] record(SharedPreferences prefs, int score) {
        int[] existing = load(prefs);
        List<Integer> values = new ArrayList<>(existing.length + 1);
        for (int value : existing) values.add(value);
        values.add(Math.max(0, score));
        Collections.sort(values, Collections.reverseOrder());
        StringBuilder saved = new StringBuilder();
        int count = Math.min(10, values.size());
        for (int index = 0; index < count; index++) {
            if (index > 0) saved.append(',');
            saved.append(values.get(index));
        }
        prefs.edit().putString(KEY, saved.toString()).apply();
        return load(prefs);
    }
}
