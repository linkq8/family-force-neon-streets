using System;
using System.IO;
using System.Reflection;
using System.Collections.Generic;
using UnityEditor;
using UnityEngine;

namespace FamilyForce.Unity.Editor
{
    public sealed class Essa221TextureImporter : AssetPostprocessor
    {
        void OnPreprocessTexture()
        {
            if(!assetPath.Contains("/PracticalRetro/Essa220/")) return;
            var t=(TextureImporter)assetImporter;
            t.textureType=TextureImporterType.Default;t.mipmapEnabled=false;t.alphaIsTransparency=true;
            t.npotScale=TextureImporterNPOTScale.None;t.maxTextureSize=2048;
            t.wrapMode=TextureWrapMode.Clamp;t.filterMode=FilterMode.Bilinear;
            t.textureCompression=TextureImporterCompression.Uncompressed;
            var android=t.GetPlatformTextureSettings("Android");
            android.overridden=true;android.maxTextureSize=2048;android.format=TextureImporterFormat.RGBA32;
            t.SetPlatformTextureSettings(android);
        }
    }
    public static class Essa221Validation
    {
        public static void Run()
        {
            void Check(bool pass,string message) { if(!pass) throw new Exception("Essa221: "+message); }
            string[] actions={"idle","walk","punch","kick","knockdown","block"};
            int[] counts={12,12,14,18,28,13};
            for(int k=0;k<actions.Length;k++)
            {
                var frames=CharacterAtlasCatalog.LoadClip("Essa",actions[k]);
                Check(frames.Length==counts[k],actions[k]+" count");
                Check(VideoEssaClips.Timing("Essa",actions[k]).Length==frames.Length,"Timing count");
                foreach(var f in frames)
                {
                    Check(f.name.StartsWith("Essa220_"),"Wrong source");
                    Check(f.rect.size==new Vector2(256,256),"Rect changed");
                    Check(Vector2.Distance(f.pivot,new Vector2(256f*7/12,32))<.001f,"Pivot changed");
                    Check(f.pixelsPerUnit==150,"Scale changed");
                    Check(f.texture.width<=1024 && f.texture.height<=1024,"Texture resized");
                }
            }
            Check(!VideoEssaClips.TryLoad("Adam","walk",out _),"Adam replaced");
            Check(CharacterAtlasCatalog.LoadClip("Essa","hurt")[0].name.StartsWith("Essa198_"),"Experimental hurt leaked");
            var go=new GameObject("Essa221 test");go.AddComponent<SpriteRenderer>();var anim=go.AddComponent<SpriteStripAnimator>();
            var idle=CharacterAtlasCatalog.LoadClip("Essa","idle");var walk=CharacterAtlasCatalog.LoadClip("Essa","walk");
            var advance=typeof(SpriteStripAnimator).GetMethod("Advance",BindingFlags.NonPublic|BindingFlags.Instance);
            void Tick(float dt) => advance.Invoke(anim,new object[]{dt});
            anim.Initialize(idle,walk,VideoEssaClips.Timing("Essa","idle"),VideoEssaClips.Timing("Essa","walk"));
            Tick(.1f);Check(anim.CurrentFrame==0,"Idle ignored duration");
            Tick(.07f);Check(anim.CurrentFrame==1,"Idle failed to advance");
            anim.SetMoving(true);Tick(.124f);Check(anim.CurrentFrame==0,"Walk duration ignored");
            Tick(.002f);Check(anim.CurrentFrame==1,"Walk duration missed");
            int saved=anim.CurrentFrame;
            var punch=CharacterAtlasCatalog.LoadClip("Essa","punch");
            anim.PlayOnce(punch,VideoEssaClips.Timing("Essa","punch"));
            var seen=new HashSet<int>();
            for(int i=0;i<116;i++){seen.Add(anim.CurrentFrame);Tick(.01f);}
            Check(seen.Count==14,"Punch frames skipped");Tick(.03f);
            Check(!anim.IsPlayingAction && anim.CurrentFrame==saved,"Walk resume broken");
            anim.PlayOnce(CharacterAtlasCatalog.LoadClip("Essa","knockdown"),VideoEssaClips.Timing("Essa","knockdown"),true);
            Tick(4);Check(anim.IsPlayingAction && anim.CurrentFrame==27,"Fall did not hold final frame");
            anim.StopAction();Check(!anim.IsPlayingAction,"Respawn did not reset");
            UnityEngine.Object.DestroyImmediate(go);
            Directory.CreateDirectory("Builds/EssaVideo221");
            File.WriteAllText("Builds/EssaVideo221/validation.json","{\"status\":\"PASS\",\"clips\":6,\"frames\":97,\"variable_timing\":true,\"punch_frames_seen\":14,\"walk_resume\":true,\"fall_hold\":true,\"experimental_hurt_excluded\":true}");
            Debug.Log("ESSA221_VALIDATION_PASS");
        }
    }
}
