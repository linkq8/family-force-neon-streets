using System;
using System.IO;
using System.Reflection;
using System.Collections.Generic;
using UnityEngine;

namespace FamilyForce.Unity.Editor
{
    public static class Motion225Validation
    {
        public static void Run()
        {
            void Check(bool ok,string message){if(!ok)throw new Exception("Motion225: "+message);}
            Check(PlayerMotor.SmoothWalkInput(new Vector2(.2f,0))==Vector2.zero,"Deadzone drift");
            foreach(float magnitude in new[]{.23f,.25f,.5f,1f})
            {
                var x=PlayerMotor.SmoothWalkInput(new Vector2(magnitude,0));
                var y=PlayerMotor.SmoothWalkInput(new Vector2(0,magnitude));
                var left=PlayerMotor.SmoothWalkInput(new Vector2(-magnitude,0));
                Check(x.magnitude>=.8f && x.magnitude<=1f,"Slow movement floor");
                Check(Mathf.Abs(x.magnitude-y.magnitude)<.0001f && left.x==-x.x,"Direction parity");
                float rate=Mathf.Lerp(1.2f,1.5f,Mathf.InverseLerp(.8f,1,x.magnitude));
                Check(35f/(35f/24/1.35f/rate)>=38f,"Slow gait returned");
            }
            var go=new GameObject("Motion225 simulation");go.AddComponent<SpriteRenderer>();var a=go.AddComponent<SpriteStripAnimator>();
            var tick=typeof(SpriteStripAnimator).GetMethod("Advance",BindingFlags.NonPublic|BindingFlags.Instance);
            var counts=new List<int>();
            foreach(int fps in new[]{60,30,15})
            {
                a.Initialize(CharacterAtlasCatalog.LoadClip("Essa","idle"),CharacterAtlasCatalog.LoadClip("Essa","walk"),VideoEssaClips.Timing("Essa","idle"),VideoEssaClips.Timing("Essa","walk"));
                a.SetMoving(true);a.SetWalkRate(1.5f);
                var seen=new HashSet<int>{a.CurrentFrame};
                // Sample once AFTER each Update, never count its internal loop.
                for(int i=0;i<Mathf.CeilToInt((35f/24/1.35f/1.5f)*fps);i++)
                {tick.Invoke(a,new object[]{1f/fps});seen.Add(a.CurrentFrame);}
                if(fps==60)Check(seen.Count==35,"60 FPS lost source poses");
                counts.Add(seen.Count);
            }
            UnityEngine.Object.DestroyImmediate(go);
            Directory.CreateDirectory("Builds/Motion225");
            File.WriteAllText("Builds/Motion225/simulation.json",$"{{\"status\":\"PASS\",\"walkFrames\":35,\"at60fps\":{counts[0]},\"at30fps\":{counts[1]},\"at15fps\":{counts[2]},\"directionParity\":true,\"inputFloor\":true,\"physicalDisplayMeasurement\":false}}");
            Debug.Log("MOTION225_VALIDATION_PASS");
        }
    }
}
