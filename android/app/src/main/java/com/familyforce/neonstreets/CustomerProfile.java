package com.familyforce.neonstreets;

import android.content.Context;
import android.graphics.Color;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;

/** Read-only, backwards-compatible view of the per-customer configuration. */
final class CustomerProfile {
    static final int HERO_COUNT = 4;
    static final String DEFAULT_APP_NAME = "Family Force: Neon Streets";
    static final String DEFAULT_EVENT_TITLE = "FAMILY FORCE";
    static final String DEFAULT_INTRO = "THE FAMILY ADVENTURE BEGINS";
    static final String DEFAULT_OUTRO = "FAMILY FORCE FOREVER!";
    static final String DEFAULT_LOGO_ASSET = "ui/logo.png";
    static final String DEFAULT_ICON_REF = "default";

    final String orderId;
    /** Kept for source compatibility; equivalent to eventTitle. */
    final String eventName;
    final String appDisplayName;
    final String eventTitle;
    final String introMessage;
    final String outroMessage;
    final Theme theme;
    final String logoAsset;
    final String appIconRef;
    final String[] heroNames;
    final String[] heroAssetStems;

    static final class Theme {
        final int primaryColor;
        final int accentColor;
        final int backgroundColor;
        final int textColor;

        private Theme(int primaryColor, int accentColor, int backgroundColor, int textColor) {
            this.primaryColor = primaryColor;
            this.accentColor = accentColor;
            this.backgroundColor = backgroundColor;
            this.textColor = textColor;
        }
    }

    private CustomerProfile(String orderId, String appDisplayName, String eventTitle,
                            String introMessage, String outroMessage, Theme theme,
                            String logoAsset, String appIconRef, String[] heroNames,
                            String[] heroAssetStems) {
        this.orderId = orderId;
        this.eventName = eventTitle;
        this.appDisplayName = appDisplayName;
        this.eventTitle = eventTitle;
        this.introMessage = introMessage;
        this.outroMessage = outroMessage;
        this.theme = theme;
        this.logoAsset = logoAsset;
        this.appIconRef = appIconRef;
        this.heroNames = heroNames;
        this.heroAssetStems = heroAssetStems;
    }

    static CustomerProfile load(Context context) {
        String[] defaultNames = {"ESSA", "ADAM", "SHAIKHA", "SULAIMAN"};
        String[] defaultStems = {"parent", "adam", "shaikha", "sulaiman"};
        try (InputStream input = context.getAssets().open("customer.json")) {
            ByteArrayOutputStream bytes = new ByteArrayOutputStream();
            byte[] buffer = new byte[4096];
            int read;
            while ((read = input.read(buffer)) != -1) bytes.write(buffer, 0, read);
            JSONObject root = new JSONObject(bytes.toString(StandardCharsets.UTF_8.name()));
            JSONArray heroes = root.getJSONArray("heroes");
            if (heroes.length() != HERO_COUNT) throw new IllegalArgumentException("hero count");
            String[] names = new String[HERO_COUNT];
            String[] stems = new String[HERO_COUNT];
            for (int i = 0; i < HERO_COUNT; i++) {
                JSONObject hero = heroes.getJSONObject(i);
                names[i] = safeText(hero.optString("displayName"), defaultNames[i], 40);
                stems[i] = safeToken(hero.optString("assetStem"), defaultStems[i]);
            }
            JSONObject branding = root.optJSONObject("branding");
            if (branding == null) branding = new JSONObject();
            JSONObject themeJson = branding.optJSONObject("theme");
            if (themeJson == null) themeJson = new JSONObject();
            String legacyEventName = safeText(root.optString("eventName"), DEFAULT_EVENT_TITLE, 80);
            String eventTitle = safeText(branding.optString("eventTitle"), legacyEventName, 80);
            Theme theme = new Theme(
                    safeColor(themeJson.optString("primary"), 0xFF15D8FF),
                    safeColor(themeJson.optString("accent"), 0xFFFF3DAE),
                    safeColor(themeJson.optString("background"), 0xFF090B22),
                    safeColor(themeJson.optString("text"), 0xFFFFFFFF));
            return new CustomerProfile(
                    safeToken(root.optString("orderId"), BuildConfig.CUSTOMER_ID),
                    safeText(branding.optString("appDisplayName"), DEFAULT_APP_NAME, 80),
                    eventTitle,
                    safeText(branding.optString("introMessage"), DEFAULT_INTRO, 160),
                    safeText(branding.optString("outroMessage"), DEFAULT_OUTRO, 160),
                    theme,
                    safeAssetPath(branding.optString("logoAsset"), DEFAULT_LOGO_ASSET),
                    safeAssetPath(branding.optString("appIconRef"), DEFAULT_ICON_REF),
                    names, stems);
        } catch (Exception ignored) {
            return defaults(defaultNames, defaultStems);
        }
    }

    private static CustomerProfile defaults(String[] names, String[] stems) {
        return new CustomerProfile(BuildConfig.CUSTOMER_ID, DEFAULT_APP_NAME,
                DEFAULT_EVENT_TITLE, DEFAULT_INTRO, DEFAULT_OUTRO,
                new Theme(0xFF15D8FF, 0xFFFF3DAE, 0xFF090B22, 0xFFFFFFFF),
                DEFAULT_LOGO_ASSET, DEFAULT_ICON_REF, names, stems);
    }

    private static String safeText(String value, String fallback, int maxLength) {
        if (value == null) return fallback;
        String clean = value.trim().replaceAll("[\\p{Cntrl}&&[^\\n]]", "");
        return clean.isEmpty() || clean.length() > maxLength ? fallback : clean;
    }

    private static String safeToken(String value, String fallback) {
        if (value == null) return fallback;
        String clean = value.trim();
        return clean.matches("[a-z0-9][a-z0-9_-]{0,39}") ? clean : fallback;
    }

    private static String safeAssetPath(String value, String fallback) {
        if (value == null) return fallback;
        String clean = value.trim();
        if (clean.equals("default")) return clean;
        if (clean.length() > 120 || clean.startsWith("/") || clean.contains("..")
                || !clean.matches("[A-Za-z0-9_./-]+\\.(png|webp)")) return fallback;
        return clean;
    }

    private static int safeColor(String value, int fallback) {
        if (value == null || !value.matches("#[0-9A-Fa-f]{6}([0-9A-Fa-f]{2})?")) return fallback;
        try {
            if (value.length() == 7) return Color.parseColor(value);
            long rgba = Long.parseLong(value.substring(1), 16);
            return (int) (((rgba & 0xFF) << 24) | (rgba >>> 8));
        } catch (RuntimeException ignored) {
            return fallback;
        }
    }
}
