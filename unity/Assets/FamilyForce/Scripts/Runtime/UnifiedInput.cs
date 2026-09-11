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

        public string DeviceLabel => ControllerRouter.Device(playerIndex) != null
            ? ControllerRouter.Device(playerIndex).displayName
            : allowTouch && TouchInputOverlay.IsAvailable
                ? "TOUCH"
                : playerIndex == 0 ? "REMOTE / KEYBOARD" : "GAMEPAD 2 / WASD";

        public bool HasAssignedGamepad
        {
            get
            {
                ClaimAssignedGamepad();
                return ControllerRouter.Device(playerIndex)!=null || !string.IsNullOrEmpty(ControllerRouter.LegacyName(playerIndex));
            }
        }

        public void ClaimAssignedGamepad()
        {
            assignedGamepad = ControllerRouter.Device(playerIndex) as Gamepad;
        }

        public Vector2 ReadMove()
        {
            ClaimAssignedGamepad();
            Vector2 move = allowTouch ? TouchInputOverlay.Move : Vector2.zero;
            Vector2 extra=ControllerRouter.ExtraMove(playerIndex);
            if(extra.sqrMagnitude>move.sqrMagnitude)move=extra;
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
                || ControllerRouter.ExtraButton(playerIndex,0)
                || (assignedGamepad != null && assignedGamepad.buttonSouth.wasPressedThisFrame)
                || (playerIndex == 0
                    ? Pressed(Keyboard.current?.enterKey)
                        || Pressed(Keyboard.current?.numpadEnterKey)
                        || Pressed(Keyboard.current?.spaceKey)
                        || UnityEngine.Input.GetKeyDown(KeyCode.Return)
                        || UnityEngine.Input.GetKeyDown(KeyCode.KeypadEnter)
                    : Pressed(Keyboard.current?.leftShiftKey));
        }

        public bool CancelPressed()
        {
            ClaimAssignedGamepad();
            return (allowTouch && TouchInputOverlay.CancelPressedThisFrame)
                || ControllerRouter.ExtraButton(playerIndex,9)
                || (assignedGamepad != null && assignedGamepad.startButton.wasPressedThisFrame)
                || Pressed(Keyboard.current?.escapeKey)
                || Pressed(Keyboard.current?.backspaceKey)
                || UnityEngine.Input.GetKeyDown(KeyCode.Escape)
                || (playerIndex == 0 && UnityEngine.Input.GetKeyDown(KeyCode.Escape));
        }

        public bool PunchPressed()
        {
            ClaimAssignedGamepad();
            return (allowTouch && TouchInputOverlay.PunchPressedThisFrame)
                || ControllerRouter.ExtraButton(playerIndex,2)
                || (assignedGamepad != null && assignedGamepad.buttonWest.wasPressedThisFrame)
                || Pressed(playerIndex == 0 ? Keyboard.current?.jKey : Keyboard.current?.fKey);

        }

        public bool JumpPressed()
        {
            ClaimAssignedGamepad();
            return (allowTouch && TouchInputOverlay.JumpPressedThisFrame)
                || ControllerRouter.ExtraButton(playerIndex,0)
                || (assignedGamepad != null && assignedGamepad.buttonSouth.wasPressedThisFrame)
                || Pressed(playerIndex == 0 ? Keyboard.current?.kKey : Keyboard.current?.spaceKey);
        }

        public bool KickPressed()
        {
            ClaimAssignedGamepad();
            return (allowTouch && TouchInputOverlay.KickPressedThisFrame)
                || ControllerRouter.ExtraButton(playerIndex,3)
                || (assignedGamepad != null && assignedGamepad.buttonNorth.wasPressedThisFrame)
                || Pressed(playerIndex == 0 ? Keyboard.current?.lKey : Keyboard.current?.rKey);
        }

        public bool HeavyPressed()
        {
            ClaimAssignedGamepad();
            return (allowTouch && TouchInputOverlay.HeavyPressedThisFrame)
                || ControllerRouter.ExtraButton(playerIndex,6)
                || (assignedGamepad != null && assignedGamepad.leftTrigger.wasPressedThisFrame)
                || Pressed(playerIndex == 0 ? Keyboard.current?.uKey : Keyboard.current?.qKey);
        }

        public bool SpecialPressed()
        {
            ClaimAssignedGamepad();
            return (allowTouch && TouchInputOverlay.SpecialPressedThisFrame)
                || ControllerRouter.ExtraButton(playerIndex,5)
                || (assignedGamepad != null && assignedGamepad.rightShoulder.wasPressedThisFrame)
                || Pressed(playerIndex == 0 ? Keyboard.current?.iKey : Keyboard.current?.eKey);
        }

        public bool GrabPressed()
        {
            ClaimAssignedGamepad();
            return (allowTouch && TouchInputOverlay.GrabPressedThisFrame)
                || ControllerRouter.ExtraButton(playerIndex,7)
                || (assignedGamepad != null && assignedGamepad.rightTrigger.wasPressedThisFrame)
                || Pressed(playerIndex == 0 ? Keyboard.current?.gKey : Keyboard.current?.cKey);
        }

        public bool TeamPressed()
        {
            ClaimAssignedGamepad();
            return (allowTouch && TouchInputOverlay.TeamPressedThisFrame)
                || ControllerRouter.ExtraButton(playerIndex,4)
                || (assignedGamepad != null && assignedGamepad.leftShoulder.wasPressedThisFrame)
                || Pressed(playerIndex == 0 ? Keyboard.current?.tKey : Keyboard.current?.vKey);
        }

        public bool WeaponPressed()
        {
            ClaimAssignedGamepad();
            return (allowTouch && TouchInputOverlay.WeaponPressedThisFrame)
                || ControllerRouter.ExtraButton(playerIndex,1)
                || (assignedGamepad != null && assignedGamepad.buttonEast.wasPressedThisFrame)
                || Pressed(playerIndex == 0 ? Keyboard.current?.oKey : Keyboard.current?.bKey);
        }

        public bool ThrowPressed()
        {
            ClaimAssignedGamepad();
            return (allowTouch && TouchInputOverlay.ThrowPressedThisFrame)
                || ControllerRouter.ExtraButton(playerIndex,11)
                || (assignedGamepad != null && assignedGamepad.rightStickButton.wasPressedThisFrame)
                || Pressed(playerIndex == 0 ? Keyboard.current?.pKey : Keyboard.current?.nKey);
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
