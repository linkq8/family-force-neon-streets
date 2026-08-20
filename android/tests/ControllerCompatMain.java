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
        System.out.println("ControllerCompat tests passed");
    }
}
