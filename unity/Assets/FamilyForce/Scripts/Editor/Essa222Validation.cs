using System;
using System.IO;
using System.Reflection;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;

namespace FamilyForce.Unity.Editor
{
    public static class Essa222Validation
    {
        public static void Run()
        {
            void Check(bool p,string m){if(!p)throw new Exception("Essa222: "+m);}
            string[] actions={"idle","walk","punch","kick","knockdown","block"};
            int[] counts={12,12,14,18,28,13};
            float[] totals={2f/1.15f,(35f/24)/1.35f,(28f/24)/2f,1.5f/2.2f,(68f/24)/1.8f,(26f/24)/1.6f};
            for(int k=0;k<actions.Length;k++)
            {
                var frames=CharacterAtlasCatalog.LoadClip("Essa",actions[k]);
                Check(frames.Length==counts[k],"Frame count");
                Check(Mathf.Abs(VideoEssaClips.FrameStart("Essa",actions[k],frames.Length)-totals[k])<.0001f,"Duration "+actions[k]);
                foreach(var frame in frames)
                {
                    Check(frame.name.StartsWith("Essa222_"),"Wrong resource");
                    Check(frame.rect.size==new Vector2(384,384),"HD cell lost");
                    Check(frame.pivot==new Vector2(224,48),"Pivot changed");
                    Check(Mathf.Abs(384f/frame.pixelsPerUnit-256f/150f)<.0001f,"World size changed");
                    Check(frame.texture.width<=1536 && frame.texture.height<=1536,"Page size changed");
                    Check(frame.texture.filterMode==FilterMode.Bilinear,"Runtime filtering");
                    var importer=(TextureImporter)AssetImporter.GetAtPath(AssetDatabase.GetAssetPath(frame.texture));
                    Check(importer.filterMode==FilterMode.Bilinear,"Importer conflict returned");
                    Check(!importer.mipmapEnabled && importer.npotScale==TextureImporterNPOTScale.None,"Unexpected scaling");
                }
            }
            Check(Mathf.Abs(VideoEssaClips.FrameStart("Essa","punch",5)-.2083333f)<.0001f,"Punch contact");
            Check(Mathf.Abs(VideoEssaClips.FrameStart("Essa","kick",6)-.2272727f)<.0001f,"Kick contact");
            var go=new GameObject("222 test");go.AddComponent<SpriteRenderer>();var anim=go.AddComponent<SpriteStripAnimator>();
            var advance=typeof(SpriteStripAnimator).GetMethod("Advance",BindingFlags.NonPublic|BindingFlags.Instance);
            void Tick(float t)=>advance.Invoke(anim,new object[]{t});
            anim.Initialize(CharacterAtlasCatalog.LoadClip("Essa","idle"),CharacterAtlasCatalog.LoadClip("Essa","walk"),VideoEssaClips.Timing("Essa","idle"),VideoEssaClips.Timing("Essa","walk"));
            anim.SetMoving(true);Tick(.4f);int saved=anim.CurrentFrame;
            anim.PlayOnce(CharacterAtlasCatalog.LoadClip("Essa","punch"),VideoEssaClips.Timing("Essa","punch"));
            var seen=new HashSet<int>();for(int i=0;i<58;i++){seen.Add(anim.CurrentFrame);Tick(.01f);}
            Check(seen.Count==14,"Faster punch skipped drawings");Tick(.005f);
            Check(!anim.IsPlayingAction && anim.CurrentFrame==saved,"Walk resume changed");
            anim.PlayOnce(CharacterAtlasCatalog.LoadClip("Essa","knockdown"),VideoEssaClips.Timing("Essa","knockdown"),true);
            Tick(2);Check(anim.CurrentFrame==27 && anim.IsPlayingAction,"Fast fall final hold");
            anim.StopAction();Check(!anim.IsPlayingAction,"Respawn reset");
            UnityEngine.Object.DestroyImmediate(go);
            Directory.CreateDirectory("Builds/EssaClear222");
            File.WriteAllText("Builds/EssaClear222/validation.json","{\"status\":\"PASS\",\"frames\":97,\"cell\":384,\"bilinear_importer_and_runtime\":true,\"unchanged_world_size\":true,\"all14_punch_frames\":true,\"faster_timing_and_hit_contacts\":true,\"walk_resume\":true,\"fall_hold\":true}");
            Debug.Log("ESSA222_VALIDATION_PASS");
        }
    }
}
