using System;
using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.InputSystem.LowLevel;
namespace FamilyForce.Unity.Editor
{
    public static class Controller229Validation
    {
        public static void Run()
        {
            ControllerRouter.Reset();
            var remote=InputSystem.AddDevice<Gamepad>();
            var xbox=InputSystem.AddDevice<Gamepad>();
            try
            {
                if(ControllerRouter.Device(0)!=remote)throw new Exception("Missing remote-first setup");
                InputState.Change(xbox.leftStick,Vector2.right);
                if(ControllerRouter.Device(0)!=xbox || new UnifiedInput(0,false).ReadMove().x<.9f)
                    throw new Exception("Active Xbox did not take P1 from remote");
                ControllerRouter.SetTwoPlayerMode(true);
                InputState.Change(xbox.leftStick,Vector2.zero);
                InputState.Change(remote.leftStick,Vector2.left);
                if(ControllerRouter.Device(0)!=xbox || new UnifiedInput(1,false).ReadMove().x>-.9f)
                    throw new Exception("Two-player slots changed");
                Debug.Log("CONTROLLER229 PASS remote-first Xbox P1 takeover; fixed two-player isolation");
            }
            finally{InputSystem.RemoveDevice(remote);InputSystem.RemoveDevice(xbox);ControllerRouter.Reset();}
        }
    }
}
