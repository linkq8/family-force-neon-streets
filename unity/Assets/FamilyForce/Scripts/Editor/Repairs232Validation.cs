using System;
using System.Reflection;
using UnityEngine;
using UnityEngine.InputSystem;
namespace FamilyForce.Unity.Editor
{
    public static class Repairs232Validation
    {
        static void Check(bool ok,string label){if(!ok)throw new Exception("232: "+label);}
        public static void Run()
        {
            var punch=ActionTiming.Durations("Essa","punch",14);float total=0;foreach(float t in punch)total+=t;
            Check(Mathf.Abs(total-.28f)<.0001f,"current arcade punch duration (retimed in234)");
            Check(ActionTiming.Start("Essa","punch",14,5)<.15f,"contact synchronized");
            Check(ActionTiming.BufferWindow(.4f)>.4f,"buffer survives recovery");
            var fall=ActionTiming.Durations("Essa","knockdown",28);total=0;foreach(float t in fall)total+=t;
            Check(total>.8f&&total<1f,"fall duration");
            var go=new GameObject("232 animation");go.AddComponent<SpriteRenderer>();var anim=go.AddComponent<SpriteStripAnimator>();
            try
            {
                var idle=CharacterAtlasCatalog.LoadClip("Essa","idle");anim.Initialize(idle,idle);
                anim.PlayOnce(CharacterAtlasCatalog.LoadClip("Essa","knockdown"),fall,true);
                typeof(SpriteStripAnimator).GetMethod("Advance",BindingFlags.NonPublic|BindingFlags.Instance).Invoke(anim,new object[]{3f});
                Check(anim.IsPlayingAction&&anim.CurrentFrame==27,"dead final pose held");
            }
            finally{UnityEngine.Object.DestroyImmediate(go);}
            ControllerRouter.Reset();var remote=InputSystem.AddDevice<Gamepad>();var one=InputSystem.AddDevice<Gamepad>();var two=InputSystem.AddDevice<Gamepad>();
            try
            {
                ControllerRouter.BeginJoin();Check(ControllerRouter.Device(0)==null,"no enumeration auto join");
                Check(ControllerRouter.JoinDevice(one)&&ControllerRouter.JoinDevice(two),"two explicit joins");
                Check(ControllerRouter.Device(0)==one&&ControllerRouter.Device(1)==two&&!ControllerRouter.JoinDevice(remote),"remote excluded from full slots");
            }
            finally{InputSystem.RemoveDevice(remote);InputSystem.RemoveDevice(one);InputSystem.RemoveDevice(two);ControllerRouter.Reset();}
            Debug.Log("REPAIRS232 PASS timing, synchronized contact, recovery buffer, final death hold, remote + two explicit controller joins");
        }
    }
}
