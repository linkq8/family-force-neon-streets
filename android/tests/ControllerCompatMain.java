package com.familyforce.neonstreets;

import android.view.KeyEvent;

public final class ControllerCompatMain {
    private static void require(boolean condition, String message) {
        if (!condition) throw new AssertionError(message);
    }

    public static void main(String[] args) {
        require(ControllerCompat.family("Joy-Con 2 (L)") == ControllerCompat.Family.NINTENDO_JOYCON,
                "Joy-Con 2 detection");
        require(ControllerCompat.family("Nintendo Switch Pro Controller") == ControllerCompat.Family.NINTENDO,
                "Switch detection");
        require(ControllerCompat.family("Xbox Wireless Controller") == ControllerCompat.Family.XBOX,
                "Xbox detection");
        require(ControllerCompat.family("DualSense Wireless Controller") == ControllerCompat.Family.PLAYSTATION,
                "DualSense detection");
        require(ControllerCompat.normalizeKey("Joy-Con (R)", KeyEvent.KEYCODE_BUTTON_4)
                        == KeyEvent.KEYCODE_BUTTON_A, "single Joy-Con confirm/jump");
        require(ControllerCompat.normalizeKey("Joy-Con 2 (L)", KeyEvent.KEYCODE_BUTTON_5)
                        == KeyEvent.KEYCODE_BUTTON_L1, "single Joy-Con link");
        require(ControllerCompat.normalizeKey("Xbox Wireless Controller", KeyEvent.KEYCODE_BUTTON_4)
                        == KeyEvent.KEYCODE_BUTTON_4, "Xbox standard mapping must pass through");
        require(ControllerCompat.normalizeKey("Joy-Con (L/R)", KeyEvent.KEYCODE_BUTTON_4)
                        == KeyEvent.KEYCODE_BUTTON_4, "paired Joy-Con standard mapping must pass through");
        require(ControllerCompat.normalizeGamepadKey("DualSense Wireless Controller",
                        KeyEvent.KEYCODE_BUTTON_A, 304, true) == KeyEvent.KEYCODE_BUTTON_X,
                "legacy DualSense square scan must become X");
        require(ControllerCompat.normalizeGamepadKey("Wireless Controller",
                        KeyEvent.KEYCODE_BUTTON_B, 305, true) == KeyEvent.KEYCODE_BUTTON_A,
                "legacy DualSense cross scan must become A");
        require(ControllerCompat.normalizeGamepadKey("DualSense Wireless Controller",
                        KeyEvent.KEYCODE_BUTTON_Y, 308, true) == KeyEvent.KEYCODE_BUTTON_L1,
                "legacy DualSense L1 scan");
        require(ControllerCompat.normalizeGamepadKey("DualSense Wireless Controller",
                        KeyEvent.KEYCODE_BUTTON_X, 313, true) == KeyEvent.KEYCODE_BUTTON_START,
                "legacy DualSense options scan");
        require(ControllerCompat.normalizeGamepadKey("DualSense Wireless Controller",
                        KeyEvent.KEYCODE_BUTTON_1, 317, false) == KeyEvent.KEYCODE_BUTTON_L2,
                "DualSense touchpad throw fallback");
        require(ControllerCompat.normalizeGamepadKey("Xbox Wireless Controller",
                        KeyEvent.KEYCODE_BUTTON_A, 304, true) == KeyEvent.KEYCODE_BUTTON_A,
                "legacy PlayStation fallback must never alter Xbox");
        require(ControllerCompat.normalizeGamepadKey("DualSense Wireless Controller",
                        KeyEvent.KEYCODE_BUTTON_A, 304, false) == KeyEvent.KEYCODE_BUTTON_A,
                "standard DualSense mapping must pass through");
        require(ControllerCompat.needsXiaomiDualSenseKeyFallback(
                        "Xiaomi", "Xiaomi", "TV Stick 4K"),
                "Xiaomi TV Stick host fallback");
        require(ControllerCompat.needsXiaomiDualSenseKeyFallback(
                        "Amlogic", "MIBOX4", "MIBOX4"),
                "Mi Box host fallback");
        require(!ControllerCompat.needsXiaomiDualSenseKeyFallback(
                        "NVIDIA", "NVIDIA", "SHIELD Android TV"),
                "Shield must keep standard DualSense mapping");
        require(!ControllerCompat.needsXiaomiDualSenseKeyFallback(
                        "Sony", "BRAVIA", "BRAVIA 4K GB"),
                "Sony TV must keep standard DualSense mapping");
        System.out.println("ControllerCompat tests passed");
    }
}
