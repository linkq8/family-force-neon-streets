using System;
using System.Reflection;
using UnityEngine;
namespace FamilyForce.Unity.Editor
{
    public static class Arcade234Validation
    {
        private static void Check(bool value,string label){if(!value)throw new Exception("234: "+label);}
        public static void Run()
        {
            foreach(string actor in new[]{CharacterAtlasCatalog.Essa,CharacterAtlasCatalog.Adam})
            foreach(string action in new[]{"punch","kick","heavy_punch","special"})
            {
                var frames=CharacterAtlasCatalog.LoadClip(actor,action);
                var times=ActionTiming.Durations(actor,action,frames.Length);float total=0;
                foreach(float t in times){Check(t>=.016f && !float.IsNaN(t),"valid frame time");total+=t;}
                Check(total<=.51f,"no cinematic normal action");
                foreach(int fps in new[]{30,60})
                {
                    var go=new GameObject("234 timeline");go.AddComponent<SpriteRenderer>();var anim=go.AddComponent<SpriteStripAnimator>();
                    try{
                        anim.Initialize(frames,frames);anim.PlayOnce(frames,times);int steps=0;
                        var advance=typeof(SpriteStripAnimator).GetMethod("Advance",BindingFlags.NonPublic|BindingFlags.Instance);
                        while(anim.IsPlayingAction && steps<120){advance.Invoke(anim,new object[]{1f/fps});steps++;}
                        Check(Mathf.Abs(steps/(float)fps-total)<=1f/fps+.001f,"30/60FPS action completion");
                    }finally{UnityEngine.Object.DestroyImmediate(go);}
                }
            }
            Check(Mathf.Abs(ActionTiming.Start("Essa","punch",14,5)-.08f)<.001f,"first contact80ms");
            Check(Mathf.Abs(ActionTiming.Start("Essa","punch",14,8)-.15f)<.001f,"second contact150ms");
            Check(Mathf.Abs(ActionTiming.Start("Essa","kick",18,6)-.10f)<.001f,"kick contact100ms");
            Debug.Log("ARCADE234 PASS punch contacts80/150ms; kick100ms; all normal actions complete at30/60FPS");
        }
    }
}
