using System.Text;
using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.InputSystem.Controls;

namespace FamilyForce.Unity
{
    /// <summary>One shared player assignment across menus and actors; includes Joystick.</summary>
    public static class ControllerRouter
    {
        private static readonly InputDevice[] slots=new InputDevice[2];
        private static string[] legacyNames=new string[0];
        private static float nextNames;
        private static bool twoPlayers;
        private static bool joining;
        private static bool explicitSlots;
        private static readonly int[] joinedFrame={-1,-1};
        public static bool JoinedThisFrame(int player)=>joinedFrame[Mathf.Clamp(player,0,1)]==Time.frameCount;
        public static void SetTwoPlayerMode(bool enabled){twoPlayers=enabled;joining=false;explicitSlots=false;}
        public static void BeginJoin(){twoPlayers=true;joining=explicitSlots=true;slots[0]=slots[1]=null;}
        public static void EndJoin(){joining=false;}
        public static bool JoinDevice(InputDevice device)
        {
            if(!twoPlayers || !explicitSlots || device==null || !(device is Gamepad || device is Joystick) || device==slots[0] || device==slots[1])return false;
            int free=slots[0]==null?0:slots[1]==null?1:-1;if(free<0)return false;slots[free]=device;joinedFrame[free]=Time.frameCount;return true;
        }
        public static void PollJoin()
        {
            if(!twoPlayers || !explicitSlots)return;
            foreach(var d in InputSystem.devices)
            {
                if(!d.enabled || d==slots[0] || d==slots[1])continue;
                bool pressed=d is Gamepad p?p.buttonSouth.wasPressedThisFrame:d is Joystick j&&j.trigger.wasPressedThisFrame;
                if(!pressed)continue;
                JoinDevice(d);
            }
        }
        private static float StickMagnitude(InputDevice d) => d is Gamepad p ? p.leftStick.ReadValue().magnitude : d is Joystick j ? j.stick.ReadValue().magnitude : 0;
        private static bool Actuated(InputDevice d)
        {
            if(d==null)return false;
            if(StickMagnitude(d)>.22f)return true;
            if(d is Gamepad p)return p.dpad.ReadValue().sqrMagnitude>.2f || p.buttonSouth.isPressed || p.buttonWest.isPressed || p.buttonNorth.isPressed || p.buttonEast.isPressed || p.startButton.isPressed || p.leftShoulder.isPressed || p.rightShoulder.isPressed || p.leftTrigger.isPressed || p.rightTrigger.isPressed;
            return d is Joystick j && j.trigger.isPressed;
        }
        // AndroidJoystick inherits a generic HID state layout; explicitly bind
        // the documented Android AGC axes/button offsets instead.
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.BeforeSceneLoad)]
        public static void ConfigureAndroidJoystick()
        {
#if UNITY_ANDROID || UNITY_EDITOR
            var json=new StringBuilder("{\"name\":\"FFAndroidJoystick226\",\"extend\":\"AndroidJoystick\",\"controls\":[");
            json.Append("{\"name\":\"stick\",\"layout\":\"Stick\",\"offset\":28,\"format\":\"VEC2\"},");
            json.Append("{\"name\":\"stick/y\",\"parameters\":\"invert\"},");
            json.Append("{\"name\":\"trigger\",\"offset\":0,\"bit\":96,\"format\":\"BIT\"}");
            int[] codes={96,97,99,100,102,103,104,105,109,108,106,107};
            for(int i=0;i<codes.Length;i++)json.Append($",{{\"name\":\"button{i}\",\"layout\":\"Button\",\"offset\":0,\"bit\":{codes[i]},\"format\":\"BIT\"}}");
            json.Append("]}");InputSystem.RegisterLayoutOverride(json.ToString());
#endif
        }
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.SubsystemRegistration)]
        public static void Reset(){slots[0]=slots[1]=null;nextNames=0;legacyNames=new string[0];twoPlayers=joining=explicitSlots=false;}
        public static InputDevice Device(int player)
        {
            for(int i=0;i<2;i++)if(slots[i]!=null&&(!slots[i].added||!slots[i].enabled))slots[i]=null;
            if(twoPlayers&&explicitSlots){PollJoin();return slots[Mathf.Clamp(player,0,1)];}
            foreach(var d in InputSystem.devices)
            {
                if(!(d is Gamepad || d is Joystick)||!d.enabled||d==slots[0]||d==slots[1])continue;
                int free=slots[0]==null?0:slots[1]==null?1:-1;
                if(free>=0){slots[free]=d;Debug.Log($"FF_CONTROLLER P{free+1} {d.displayName} layout={d.layout}");}
            }
            // Android TV remotes can occupy a Gamepad slot before the real pad.
            // Single-player follows deliberate activity, not enumeration order.
            if(!twoPlayers)
                foreach(var d in InputSystem.devices)
                {
                    if(d==slots[0] || !d.enabled || !(d is Gamepad || d is Joystick))continue;
                    if(Actuated(d) && (!Actuated(slots[0]) || (StickMagnitude(d)>.22f && StickMagnitude(slots[0])<=.22f)))
                    {
                        var old=slots[0];if(slots[1]==d)slots[1]=old;slots[0]=d;
                        Debug.Log($"FF_CONTROLLER ACTIVE P1 {d.displayName}");break;
                    }
                }
            return slots[Mathf.Clamp(player,0,1)];
        }
        public static string LegacyName(int player)
        {
            if(Time.unscaledTime>=nextNames){legacyNames=Input.GetJoystickNames();nextNames=Time.unscaledTime+.5f;}
            return player<legacyNames.Length?legacyNames[player]:"";
        }
        public static Vector2 ExtraMove(int player)
        {
            var d=Device(player);Vector2 move=Vector2.zero;
            if(d is Joystick stick)
            {
                move=stick.stick.ReadValue();
                if(stick.hatswitch!=null){var hat=stick.hatswitch.ReadValue();if(hat.sqrMagnitude>move.sqrMagnitude)move=hat;}
            }
            // Old Android/OEM drivers can appear only in the legacy joystick API.
            if(d == null && !string.IsNullOrEmpty(LegacyName(player)))
            {
                var legacy=new Vector2(Input.GetAxisRaw($"FF_P{player+1}_X"),Input.GetAxisRaw($"FF_P{player+1}_Y"));
                if(legacy.sqrMagnitude>move.sqrMagnitude)move=legacy;
            }
            return Vector2.ClampMagnitude(move,1);
        }
        public static bool ExtraButton(int player,int button)
        {
            var d=Device(player);if(d is Gamepad)return false;
            if(d is Joystick j)
            {
                var c=j.TryGetChildControl<ButtonControl>($"button{button}");
                if(c!=null&&c.wasPressedThisFrame)return true;
                if(button==0 && j.trigger.wasPressedThisFrame)return true;
            }
            return d == null && !string.IsNullOrEmpty(LegacyName(player)) && Input.GetKeyDown((KeyCode)((int)KeyCode.Joystick1Button0+player*20+button));
        }
        public static string Diagnostics()
        {
            var s=new StringBuilder();
            s.AppendLine($"Mode: {(twoPlayers?"2 players / fixed slots":"1 player / active controller")} | Render: {Screen.width}x{Screen.height}");
            for(int i=0;i<2;i++)
            {
                var d=Device(i);var move=d is Gamepad p?p.leftStick.ReadValue():ExtraMove(i);
                s.AppendLine($"P{i+1}: {(d==null?"No Input System controller":d.displayName)}  [{d?.layout}]");
                s.AppendLine($"Stick: {move.x:0.00}, {move.y:0.00}   Legacy: {LegacyName(i)}");
                if(d!=null){s.Append("Held: ");foreach(var c in d.allControls)if(c is ButtonControl b&&b.isPressed)s.Append(c.name+" ");s.AppendLine();}
            }
            if(slots[0]==null)s.AppendLine("No controller detected: pair it in Android Bluetooth / connect USB, then return.");
            s.AppendLine("South: confirm/jump | West: punch | North: kick | East: weapon");
            s.AppendLine("START: menu | L1: team | R1: special | L2: heavy | R2: grab");
            s.Append("Generic / Joy-Con mappings depend on Android. Separate Joy-Cons are not merged.");
            return s.ToString();
        }
    }
}
