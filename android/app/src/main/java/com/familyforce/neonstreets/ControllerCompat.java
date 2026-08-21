package com.familyforce.neonstreets;

import android.view.KeyEvent;

import java.util.Locale;

/** Small compatibility layer over Android's standard game-controller mapping. */
final class ControllerCompat {
    enum Family { NINTENDO_JOYCON, NINTENDO, XBOX, PLAYSTATION, GENERIC }

    private ControllerCompat() {}

    static Family family(String deviceName) {
        String name = normalizedName(deviceName);
        if (name.contains("joy-con") || name.contains("joycon")
                || name.contains("joy con")) return Family.NINTENDO_JOYCON;
        if (name.contains("nintendo") || name.contains("switch")) return Family.NINTENDO;
        if (name.contains("xbox") || name.contains("x-input") || name.contains("xinput")) {
            return Family.XBOX;
        }
        if (name.contains("dualsense") || name.contains("dualshock")
                || name.contains("wireless controller") || name.contains("playstation")) {
            return Family.PLAYSTATION;
        }
        return Family.GENERIC;
    }

    static boolean isSingleJoyCon(String deviceName) {
        String name = normalizedName(deviceName);
        if (family(name) != Family.NINTENDO_JOYCON) return false;
        if (name.contains("pair") || name.contains("combined") || name.contains("grip")
                || name.contains("l/r") || name.contains("left/right")) return false;
        return name.contains("(l)") || name.contains("(r)") || name.contains("left")
                || name.contains("right") || name.contains("joy-con 2")
                || name.contains("joycon 2") || name.contains("joy con 2");
    }

    /** Narrow fallback for Xiaomi Android TV builds missing AOSP's DualSense key layout. */
    static boolean needsXiaomiDualSenseKeyFallback(String manufacturer, String brand,
                                                    String model) {
        String host = normalizedName(manufacturer) + " " + normalizedName(brand)
                + " " + normalizedName(model);
        return host.contains("xiaomi") || host.contains("mibox") || host.contains("mi box")
                || host.contains("mistick") || host.contains("mi stick")
                || host.contains("mitv") || host.contains("mi tv");
    }

    /**
     * Some Android/TV Bluetooth stacks expose a sideways single Joy-Con's face
     * and SL/SR buttons as generic BUTTON_1..8. Convert only that fallback;
     * standardized BUTTON_A/B/X/Y and shoulder events pass through untouched.
     */
    static int normalizeKey(String deviceName, int keyCode) {
        return normalizeKey(deviceName, keyCode, 0, false);
    }

    /**
     * Older Android TV images can miss AOSP's DualSense fallback .kl file.
     * In that case Linux scan codes reach Generic.kl and face/shoulder buttons
     * are assigned to the wrong Android key codes. The scan mapping below is
     * the same mapping used by AOSP's Vendor_054c_Product_0ce6_fallback.kl.
     */
    static int normalizeKey(String deviceName, int keyCode, int scanCode,
                            boolean legacyDualSenseLayout) {
        if (!isSingleJoyCon(deviceName)) return keyCode;
        return normalizeSingleJoyConKey(keyCode);
    }

    static int normalizeGamepadKey(String deviceName, int keyCode, int scanCode,
                                   boolean legacyDualSenseLayout) {
        if (isSingleJoyCon(deviceName)) return normalizeSingleJoyConKey(keyCode);
        if (family(deviceName) != Family.PLAYSTATION) return keyCode;
        if (legacyDualSenseLayout) {
            switch (scanCode) {
                case 304: return KeyEvent.KEYCODE_BUTTON_X;      // Square
                case 305: return KeyEvent.KEYCODE_BUTTON_A;      // Cross
                case 306: return KeyEvent.KEYCODE_BUTTON_B;      // Circle
                case 307: return KeyEvent.KEYCODE_BUTTON_Y;      // Triangle
                case 308: return KeyEvent.KEYCODE_BUTTON_L1;
                case 309: return KeyEvent.KEYCODE_BUTTON_R1;
                case 310: return KeyEvent.KEYCODE_BUTTON_L2;
                case 311: return KeyEvent.KEYCODE_BUTTON_R2;
                case 312: return KeyEvent.KEYCODE_BUTTON_SELECT;
                case 313: return KeyEvent.KEYCODE_BUTTON_START;
                case 314: return KeyEvent.KEYCODE_BUTTON_THUMBL;
                case 315: return KeyEvent.KEYCODE_BUTTON_THUMBR;
                case 316: return KeyEvent.KEYCODE_BUTTON_MODE;
                case 317: return KeyEvent.KEYCODE_BUTTON_L2;     // Touchpad = throw backup
                default: break;
            }
        }
        // AOSP exposes the DualSense touchpad click as BUTTON_1 in its
        // fallback layout. Treat it as a redundant throw control so players
        // are not blocked when an OEM drops the analog L2 axis.
        if (keyCode == KeyEvent.KEYCODE_BUTTON_1) return KeyEvent.KEYCODE_BUTTON_L2;
        return keyCode;
    }

    private static int normalizeSingleJoyConKey(int keyCode) {
        switch (keyCode) {
            case KeyEvent.KEYCODE_BUTTON_1: return KeyEvent.KEYCODE_BUTTON_X; // punch
            case KeyEvent.KEYCODE_BUTTON_2: return KeyEvent.KEYCODE_BUTTON_B; // kick/cancel
            case KeyEvent.KEYCODE_BUTTON_3: return KeyEvent.KEYCODE_BUTTON_Y; // heavy punch
            case KeyEvent.KEYCODE_BUTTON_4: return KeyEvent.KEYCODE_BUTTON_A; // jump/confirm
            case KeyEvent.KEYCODE_BUTTON_5: return KeyEvent.KEYCODE_BUTTON_L1; // Link
            case KeyEvent.KEYCODE_BUTTON_6: return KeyEvent.KEYCODE_BUTTON_R1; // special
            case KeyEvent.KEYCODE_BUTTON_7: return KeyEvent.KEYCODE_BUTTON_L2; // throw
            case KeyEvent.KEYCODE_BUTTON_8: return KeyEvent.KEYCODE_BUTTON_R2; // heavy kick
            default: return keyCode;
        }
    }

    static String label(String deviceName) {
        switch (family(deviceName)) {
            case NINTENDO_JOYCON: return "NINTENDO JOY-CON";
            case NINTENDO: return "NINTENDO SWITCH";
            case XBOX: return "XBOX CONTROLLER";
            case PLAYSTATION: return "PLAYSTATION CONTROLLER";
            default: return "GAME CONTROLLER";
        }
    }

    private static String normalizedName(String value) {
        return value == null ? "" : value.trim().toLowerCase(Locale.US);
    }
}
