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
        private readonly int playerIndex;
        private readonly bool allowTouch;
        private Gamepad assignedGamepad;

        public UnifiedInput(int index = 0, bool touch = true)
        {
            playerIndex = Mathf.Max(0, index);
            allowTouch = touch && playerIndex == 0;
        }

        public string DeviceLabel => assignedGamepad != null
            ? assignedGamepad.displayName
            : allowTouch && TouchInputOverlay.IsAvailable
                ? "TOUCH"
                : playerIndex == 0 ? "REMOTE / KEYBOARD" : "GAMEPAD 2 / WASD";

        public bool HasAssignedGamepad
        {
            get
            {
                ClaimAssignedGamepad();
                return assignedGamepad != null;
            }
        }

        public void ClaimAssignedGamepad()
        {
            if (assignedGamepad != null && !assignedGamepad.added)
                assignedGamepad = null;
            if (assignedGamepad == null && Gamepad.all.Count > playerIndex)
                assignedGamepad = Gamepad.all[playerIndex];
        }

        public Vector2 ReadMove()
        {
            ClaimAssignedGamepad();
            Vector2 move = allowTouch ? TouchInputOverlay.Move : Vector2.zero;
            if (assignedGamepad != null)
            {
                Vector2 gamepadMove = assignedGamepad.leftStick.ReadValue();
                Vector2 dpad = assignedGamepad.dpad.ReadValue();
                if (dpad.sqrMagnitude > gamepadMove.sqrMagnitude)
                    gamepadMove = dpad;
                if (gamepadMove.sqrMagnitude > move.sqrMagnitude)
                    move = gamepadMove;
            }

            Keyboard keyboard = Keyboard.current;
            if (keyboard != null)
            {
                float x = playerIndex == 0
                    ? ReadAxis(keyboard.leftArrowKey, keyboard.rightArrowKey)
                    : ReadAxis(keyboard.aKey, keyboard.dKey);
                float y = playerIndex == 0
                    ? ReadAxis(keyboard.downArrowKey, keyboard.upArrowKey)
                    : ReadAxis(keyboard.sKey, keyboard.wKey);
                Vector2 keyboardMove = new Vector2(x, y);
                if (keyboardMove.sqrMagnitude > move.sqrMagnitude)
                    move = keyboardMove;
            }

            // Several Android TV remotes are exposed only through the legacy
            // KeyEvent bridge even when the Input System package is enabled.
            Vector2 legacy = new Vector2(
                playerIndex == 0
                    ? LegacyAxis(KeyCode.LeftArrow, KeyCode.RightArrow)
                    : LegacyAxis(KeyCode.A, KeyCode.D),
                playerIndex == 0
                    ? LegacyAxis(KeyCode.DownArrow, KeyCode.UpArrow)
                    : LegacyAxis(KeyCode.S, KeyCode.W));
            if (legacy.sqrMagnitude > move.sqrMagnitude)
                move = legacy;

            return move.sqrMagnitude < DeadZone * DeadZone
                ? Vector2.zero
                : Vector2.ClampMagnitude(move, 1f);
        }

        public bool ConfirmPressed()
        {
            ClaimAssignedGamepad();
            return (allowTouch && TouchInputOverlay.ConfirmPressedThisFrame)
                || (assignedGamepad != null && assignedGamepad.buttonSouth.wasPressedThisFrame)
                || Pressed(Keyboard.current?.enterKey)
                || Pressed(Keyboard.current?.numpadEnterKey)
                || Pressed(Keyboard.current?.spaceKey)
                || UnityEngine.Input.GetKeyDown(KeyCode.Return)
                || UnityEngine.Input.GetKeyDown(KeyCode.KeypadEnter)
                || UnityEngine.Input.GetKeyDown(KeyCode.JoystickButton0);
        }

        public bool CancelPressed()
        {
            ClaimAssignedGamepad();
            return (allowTouch && TouchInputOverlay.CancelPressedThisFrame)
                || (assignedGamepad != null && assignedGamepad.buttonEast.wasPressedThisFrame)
                || Pressed(Keyboard.current?.escapeKey)
                || Pressed(Keyboard.current?.backspaceKey)
                || UnityEngine.Input.GetKeyDown(KeyCode.Escape)
                || UnityEngine.Input.GetKeyDown(KeyCode.JoystickButton1);
        }

        public bool PunchPressed()
        {
            ClaimAssignedGamepad();
            return (allowTouch && TouchInputOverlay.PunchPressedThisFrame)
                || (assignedGamepad != null && assignedGamepad.buttonWest.wasPressedThisFrame)
                || Pressed(playerIndex == 0 ? Keyboard.current?.jKey : Keyboard.current?.fKey);

        }

        public bool JumpPressed()
        {
            ClaimAssignedGamepad();
            return (allowTouch && TouchInputOverlay.JumpPressedThisFrame)
                || (assignedGamepad != null && assignedGamepad.buttonSouth.wasPressedThisFrame)
                || Pressed(playerIndex == 0 ? Keyboard.current?.kKey : Keyboard.current?.spaceKey);
        }

        public bool KickPressed()
        {
            ClaimAssignedGamepad();
            return (allowTouch && TouchInputOverlay.KickPressedThisFrame)
                || (assignedGamepad != null && assignedGamepad.buttonNorth.wasPressedThisFrame)
                || Pressed(playerIndex == 0 ? Keyboard.current?.lKey : Keyboard.current?.rKey);
        }

        public bool HeavyPressed()
        {
            ClaimAssignedGamepad();
            return (allowTouch && TouchInputOverlay.HeavyPressedThisFrame)
                || (assignedGamepad != null && assignedGamepad.leftTrigger.wasPressedThisFrame)
                || Pressed(playerIndex == 0 ? Keyboard.current?.uKey : Keyboard.current?.qKey);
        }

        public bool SpecialPressed()
        {
            ClaimAssignedGamepad();
            return (allowTouch && TouchInputOverlay.SpecialPressedThisFrame)
                || (assignedGamepad != null && assignedGamepad.rightShoulder.wasPressedThisFrame)
                || Pressed(playerIndex == 0 ? Keyboard.current?.iKey : Keyboard.current?.eKey);
        }

        public bool GrabPressed()
        {
            ClaimAssignedGamepad();
            return (allowTouch && TouchInputOverlay.GrabPressedThisFrame)
                || (assignedGamepad != null && assignedGamepad.rightTrigger.wasPressedThisFrame)
                || Pressed(playerIndex == 0 ? Keyboard.current?.gKey : Keyboard.current?.cKey);
        }

        public bool TeamPressed()
        {
            ClaimAssignedGamepad();
            return (allowTouch && TouchInputOverlay.TeamPressedThisFrame)
                || (assignedGamepad != null && assignedGamepad.leftShoulder.wasPressedThisFrame)
                || Pressed(playerIndex == 0 ? Keyboard.current?.tKey : Keyboard.current?.vKey);
        }

        private static float ReadAxis(KeyControl negative, KeyControl positive)
        {
            bool negativePressed = negative.isPressed;
            bool positivePressed = positive.isPressed;
            return negativePressed == positivePressed ? 0f : positivePressed ? 1f : -1f;
        }

        private static float LegacyAxis(KeyCode negative, KeyCode positive)
        {
            bool negativePressed = UnityEngine.Input.GetKey(negative);
            bool positivePressed = UnityEngine.Input.GetKey(positive);
            return negativePressed == positivePressed ? 0f : positivePressed ? 1f : -1f;
        }

        private static bool Pressed(ButtonControl control) =>
            control != null && control.wasPressedThisFrame;
    }
}
