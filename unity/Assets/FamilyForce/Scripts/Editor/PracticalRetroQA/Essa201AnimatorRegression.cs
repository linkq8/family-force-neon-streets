using System;
using System.Collections.Generic;
using System.IO;
using System.Reflection;
using UnityEngine;

namespace FamilyForce.Unity.Editor
{
    public static class Essa201AnimatorRegression
    {
        public static void Run()
        {
            var obj=new GameObject("Motion regression");
            obj.AddComponent<SpriteRenderer>();
            var animator=obj.AddComponent<SpriteStripAnimator>();
            var idle=CharacterAtlasCatalog.LoadClip("Essa","idle");
            var walk=CharacterAtlasCatalog.LoadClip("Essa","walk");
            var hurt=CharacterAtlasCatalog.LoadClip("Essa","hurt");
            var advance=typeof(SpriteStripAnimator).GetMethod("Advance",BindingFlags.Instance|BindingFlags.NonPublic);
            void Tick(float dt) => advance.Invoke(animator,new object[]{dt});
            void Check(bool ok,string reason) { if(!ok) throw new Exception(reason); }
            animator.Initialize(idle,walk);
            animator.SetMoving(true);
            Tick(.51f);
            int before=animator.CurrentFrame;
            Check(before==6,"Setup must be in second half of walk");
            animator.PlayOnce(hurt);
            Tick(.251f);
            Check(!animator.IsPlayingAction && animator.CurrentFrame==before,"Hurt reset the walk to frame zero");
            animator.SetMoving(false);
            animator.SetMoving(true);
            Check(animator.CurrentFrame==before,"Brief touch release reset the walk");
            var seen=new HashSet<int>();
            for(int i=0;i<150;i++)
            {
                Tick(.04f);
                if(!animator.IsPlayingAction) seen.Add(animator.CurrentFrame);
                if(i%7==0) animator.PlayOnce(hurt,new[]{.02f,.02f,.02f});
            }
            Check(seen.Count==12,"Repeated hits starved later walk frames");
            animator.Initialize(idle,walk);
            Check(!animator.IsMoving && !animator.IsPlayingAction && animator.CurrentFrame==0,"Initialize leaked old state");
            animator.SetMoving(true);
            Tick(0f);
            Check(animator.CurrentFrame==0,"Paused time advanced the animation");
            animator.PlayOnce(hurt,new[]{.05f,.1f,.2f});
            Tick(.049f);Check(animator.CurrentFrame==0,"Action anticipation too short");
            Tick(.002f);Check(animator.CurrentFrame==1,"Per-frame action duration ignored");
            string output=Path.GetFullPath("../art-pipeline/builds/Essa/motion-201/animator-regression.json");
            Directory.CreateDirectory(Path.GetDirectoryName(output));
            File.WriteAllText(output,"{\"status\":\"PASS\",\"hurt_resumes_walk\":true,\"brief_touch_release_resumes_walk\":true,\"frames_observed_under_repeated_interrupts\":12,\"initialize_resets_state\":true,\"zero_delta_pauses\":true,\"per_frame_timing\":true}");
            UnityEngine.Object.DestroyImmediate(obj);
            Debug.Log("ESSA201_ANIMATOR_REGRESSION_PASS");
        }
    }
}
