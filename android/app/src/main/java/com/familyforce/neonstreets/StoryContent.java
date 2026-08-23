package com.familyforce.neonstreets;

import android.content.Context;
import android.util.Log;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Locale;

/** Small immutable bilingual story database loaded once from APK assets. */
final class StoryContent {
    private static final String TAG = "FamilyForceStory";

    static final class Line {
        final String speaker;
        final String emotion;
        final String text;

        Line(String speaker, String emotion, String text) {
            this.speaker = speaker;
            this.emotion = emotion;
            this.text = text;
        }
    }

    private final JSONObject root;
    private final boolean rtl;

    private StoryContent(JSONObject root) {
        this.root = root;
        rtl = "rtl".equals(root.optString("direction"));
    }

    static StoryContent load(Context context) {
        String saved = context.getSharedPreferences("family_force_settings", Context.MODE_PRIVATE)
                .getString("story_language", "");
        String language = "ar".equals(saved) || "en".equals(saved)
                ? saved : ("ar".equals(Locale.getDefault().getLanguage()) ? "ar" : "en");
        try (InputStream input = context.getAssets().open("story/story_" + language + ".json")) {
            ByteArrayOutputStream bytes = new ByteArrayOutputStream();
            byte[] buffer = new byte[4096];
            int read;
            while ((read = input.read(buffer)) >= 0) bytes.write(buffer, 0, read);
            return new StoryContent(new JSONObject(bytes.toString(StandardCharsets.UTF_8.name())));
        } catch (Throwable error) {
            Log.e(TAG, "Story data unavailable; gameplay will continue", error);
            return new StoryContent(new JSONObject());
        }
    }

    boolean isRtl() {
        return rtl;
    }

    String language() {
        return root.optString("language", rtl ? "ar" : "en");
    }

    String title() {
        return root.optString("title", "Family Force: Shadow Grid");
    }

    String ui(String key, String fallback) {
        JSONObject ui = root.optJSONObject("ui");
        return ui == null ? fallback : ui.optString(key, fallback);
    }

    List<Line> scene(String id) {
        JSONObject scenes = root.optJSONObject("scenes");
        JSONArray lines = scenes == null ? null : scenes.optJSONArray(id);
        if (lines == null || lines.length() == 0) return Collections.emptyList();
        ArrayList<Line> result = new ArrayList<>(lines.length());
        for (int index = 0; index < lines.length(); index++) {
            JSONObject line = lines.optJSONObject(index);
            if (line == null) continue;
            String text = line.optString("text", "").trim();
            if (text.isEmpty()) continue;
            result.add(new Line(line.optString("speaker", "narrator"),
                    line.optString("emotion", "neutral"), text));
        }
        return Collections.unmodifiableList(result);
    }
}
