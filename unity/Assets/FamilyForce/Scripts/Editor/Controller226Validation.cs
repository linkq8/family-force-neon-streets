using System;
using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.InputSystem.LowLevel;

namespace FamilyForce.Unity.Editor
{
    public static class Controller226Validation
    {
        private static void Check(bool value,string message){if(!value)throw new Exception("Controller226: "+message);}
        private static void Set<T>(InputControl<T> control,T value) where T:struct
        {
            using(StateEvent.From(control.device,out var evt))
            {control.WriteValueIntoEvent(value,evt);InputSystem.QueueEvent(evt);}
            InputSystem.Update();
        }
        public static void Run()
        {
            ControllerRouter.ConfigureAndroidJoystick();
            var android=InputSystem.AddDevice("AndroidJoystick") as Joystick;
            try
            {
                var state=new UnityEngine.InputSystem.Android.LowLevel.AndroidGameControllerState()
                    .WithAxis(UnityEngine.InputSystem.Android.LowLevel.AndroidAxis.X,1)
                    .WithButton(UnityEngine.InputSystem.Android.LowLevel.AndroidKeyCode.ButtonA);
                InputSystem.QueueStateEvent(android,state);InputSystem.Update();
                Check(android.stick.ReadValue().x>.9f&&android.trigger.isPressed,"raw Android joystick state");
                Debug.Log("CONTROLLER226 PASS AndroidJoystick raw AGC axis and button");
            }
            finally{InputSystem.RemoveDevice(android);}
            ControllerRouter.Reset();
            foreach(string layout in new[]{"XInputController","XboxOneGamepadAndroid","DualShock4GamepadAndroid","AndroidGamepadWithDpadButtons"})
            {
                var pad=InputSystem.AddDevice(layout) as Gamepad;
                try
                {
                    Check(pad!=null,layout+" missing");
                    var input=new UnifiedInput(0,false);
                    Set(pad.leftStick,Vector2.right);
                    Check(input.ReadMove().x>.9f,layout+" stick right");
                    Set(pad.leftStick,Vector2.left);
                    Check(input.ReadMove().x<-.9f,layout+" stick left");
                    Set(pad.leftStick,Vector2.zero);
                    Set(pad.leftStick,Vector2.up);
                    Check(input.ReadMove().y>.9f,layout+" stick up");
                    Set(pad.leftStick,Vector2.zero);
                    Set(pad.dpad,Vector2.right);
                    Check(input.ReadMove().x>.9f,layout+" dpad right");
                    Set(pad.buttonSouth,0f);
                    input.ConfirmPressed();
                    Set(pad.buttonSouth,1f);
                    Check(pad.buttonSouth.isPressed,layout+" south button state");
                    Debug.Log("CONTROLLER226 PASS virtual layout "+layout);
                }
                finally{if(pad!=null)InputSystem.RemoveDevice(pad);ControllerRouter.Reset();}
            }
            var first=InputSystem.AddDevice<Joystick>();var second=InputSystem.AddDevice<Gamepad>();
            ControllerRouter.SetTwoPlayerMode(true);
            InputDevice replacement=null;
            try
            {
                Check(ControllerRouter.Device(0)==first&&ControllerRouter.Device(1)==second,"two player assignment");
                Set(first.stick,Vector2.left);
                Check(new UnifiedInput(0,false).ReadMove().x<-.9f,"generic joystick movement");
                Check(new UnifiedInput(1,false).ReadMove()==Vector2.zero,"P2 isolation");
                InputSystem.RemoveDevice(first);
                Check(ControllerRouter.Device(0)==null&&ControllerRouter.Device(1)==second,"disconnect preserves P2");
                replacement=InputSystem.AddDevice<Gamepad>();
                Check(ControllerRouter.Device(0)==replacement&&ControllerRouter.Device(1)==second,"reconnect fills P1");
                Debug.Log("CONTROLLER226 PASS generic joystick, isolation, disconnect/reconnect. No physical hardware certification.");
            }
            finally
            {
                if(first.added)InputSystem.RemoveDevice(first);
                InputSystem.RemoveDevice(second);
                if(replacement!=null)InputSystem.RemoveDevice(replacement);
                ControllerRouter.Reset();
            }
        }
    }
}
