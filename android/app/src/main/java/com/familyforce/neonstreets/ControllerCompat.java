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

    /**
     * Some Android/TV Bluetooth stacks expose a sideways single Joy-Con's face
     * and SL/SR buttons as generic BUTTON_1..8. Convert only that fallback;
     * standardized BUTTON_A/B/X/Y and shoulder events pass through untouched.
     */
    static int normalizeKey(String deviceName, int keyCode) {
        if (!isSingleJoyCon(deviceName)) return keyCode;
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
