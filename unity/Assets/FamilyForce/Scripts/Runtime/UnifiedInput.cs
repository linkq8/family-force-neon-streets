using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.InputSystem.Controls;

namespace FamilyForce.Unity
{
    /// <summary>
    /// One low-allocation input surface shared by menus and gameplay. Android
    /// TV remotes normally arrive as Keyboard/D-pad; controllers arrive as
    /// Gamepad. Device-specific OEM corrections will live behind this class.
    /// </summary>
    public sealed class UnifiedInput
    {
        private const float DeadZone = 0.22f;
        private Gamepad assignedGamepad;

        public string DeviceLabel => assignedGamepad != null
            ? assignedGamepad.displayName
            : "REMOTE / KEYBOARD";

        public void ClaimFirstAvailableGamepad()
        {
            if (assignedGamepad == null && Gamepad.all.Count > 0)
                assignedGamepad = Gamepad.all[0];
        }

        public Vector2 ReadMove()
        {
            ClaimFirstAvailableGamepad();
            Vector2 move = Vector2.zero;
            if (assignedGamepad != null)
            {
                move = assignedGamepad.leftStick.ReadValue();
                Vector2 dpad = assignedGamepad.dpad.ReadValue();
                if (dpad.sqrMagnitude > move.sqrMagnitude)
                    move = dpad;
            }

            Keyboard keyboard = Keyboard.current;
            if (keyboard != null)
            {
                float x = ReadAxis(keyboard.leftArrowKey, keyboard.rightArrowKey,
                    keyboard.aKey, keyboard.dKey);
                float y = ReadAxis(keyboard.downArrowKey, keyboard.upArrowKey,
                    keyboard.sKey, keyboard.wKey);
                Vector2 keyboardMove = new Vector2(x, y);
                if (keyboardMove.sqrMagnitude > move.sqrMagnitude)
                    move = keyboardMove;
            }

            // Several Android TV remotes are exposed only through the legacy
            // KeyEvent bridge even when the Input System package is enabled.
            Vector2 legacy = new Vector2(
                LegacyAxis(KeyCode.LeftArrow, KeyCode.RightArrow, KeyCode.A, KeyCode.D),
                LegacyAxis(KeyCode.DownArrow, KeyCode.UpArrow, KeyCode.S, KeyCode.W));
            if (legacy.sqrMagnitude > move.sqrMagnitude)
                move = legacy;

            return move.sqrMagnitude < DeadZone * DeadZone
                ? Vector2.zero
                : Vector2.ClampMagnitude(move, 1f);
        }

        public bool ConfirmPressed()
        {
            ClaimFirstAvailableGamepad();
            return (assignedGamepad != null && assignedGamepad.buttonSouth.wasPressedThisFrame)
                || Pressed(Keyboard.current?.enterKey)
                || Pressed(Keyboard.current?.numpadEnterKey)
                || Pressed(Keyboard.current?.spaceKey)
                || UnityEngine.Input.GetKeyDown(KeyCode.Return)
                || UnityEngine.Input.GetKeyDown(KeyCode.KeypadEnter)
                || UnityEngine.Input.GetKeyDown(KeyCode.JoystickButton0);
        }

        public bool CancelPressed()
        {
            ClaimFirstAvailableGamepad();
            return (assignedGamepad != null && assignedGamepad.buttonEast.wasPressedThisFrame)
                || Pressed(Keyboard.current?.escapeKey)
                || Pressed(Keyboard.current?.backspaceKey)
                || UnityEngine.Input.GetKeyDown(KeyCode.Escape)
                || UnityEngine.Input.GetKeyDown(KeyCode.JoystickButton1);
        }

        public bool PunchPressed()
        {
            ClaimFirstAvailableGamepad();
            return (assignedGamepad != null && assignedGamepad.buttonWest.wasPressedThisFrame)
                || Pressed(Keyboard.current?.jKey);

        }

        public bool JumpPressed()
        {
            ClaimFirstAvailableGamepad();
            return (assignedGamepad != null && assignedGamepad.buttonSouth.wasPressedThisFrame)
                || Pressed(Keyboard.current?.kKey);
        }

        private static float ReadAxis(KeyControl negative1, KeyControl positive1,
            KeyControl negative2, KeyControl positive2)
        {
            bool negative = negative1.isPressed || negative2.isPressed;
            bool positive = positive1.isPressed || positive2.isPressed;
            return negative == positive ? 0f : positive ? 1f : -1f;
        }

        private static float LegacyAxis(KeyCode negative1, KeyCode positive1,
            KeyCode negative2, KeyCode positive2)
        {
            bool negative = UnityEngine.Input.GetKey(negative1) || UnityEngine.Input.GetKey(negative2);
            bool positive = UnityEngine.Input.GetKey(positive1) || UnityEngine.Input.GetKey(positive2);
            return negative == positive ? 0f : positive ? 1f : -1f;
        }

        private static bool Pressed(ButtonControl control) =>
            control != null && control.wasPressedThisFrame;
    }
}
