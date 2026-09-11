using System;
using System.Collections.Generic;
using UnityEngine;

namespace FamilyForce.Unity
{
    /// <summary>Versioned video-derived art. Original timing, no repeated-pose expansion.</summary>
    public static class VideoEssaClips
    {
        [Serializable] private class Manifest { public float pixelsPerUnit; public float[] pivot; public Clip[] clips; }
        [Serializable] private class Clip { public string action; public string[] pages; public Frame[] frames; }
        [Serializable] private class Frame { public int page; public float[] rect; public float seconds; }
        private static readonly Dictionary<string, Sprite[]> Sprites = new();
        private static readonly Dictionary<string, float[]> Durations = new();
        private static bool loaded;
        private static bool failed;
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.SubsystemRegistration)]
        private static void Reset()
        {
            foreach(var frames in Sprites.Values) foreach(var s in frames) if(s!=null) UnityEngine.Object.Destroy(s);
            Sprites.Clear(); Durations.Clear(); loaded=failed=false;
        }
        public static bool TryLoad(string actor,string action,out Sprite[] frames)
        {
            frames=null;
            if(actor!=CharacterAtlasCatalog.Essa) return false;
            if(failed)return false;
            if(!loaded)
            {
                var pending=new Dictionary<string,Sprite[]>();var pendingTimes=new Dictionary<string,float[]>();
                var created=new List<Sprite>();
                try
                {
                var json=Resources.Load<TextAsset>("PracticalRetro/Essa222/clips");
                if(json==null) return false;
                var manifest=JsonUtility.FromJson<Manifest>(json.text);
                if(manifest?.clips==null || manifest.pivot==null || manifest.pivot.Length!=2 || manifest.pixelsPerUnit<=0)throw new InvalidOperationException("Invalid video manifest");
                foreach(var clip in manifest.clips)
                {
                    var active=clip;
                    string root="PracticalRetro/Essa222/",name="Essa222";
                    if(clip.action=="walk")
                    {
                        var smooth=Resources.Load<TextAsset>("PracticalRetro/Essa225/walk");
                        if(smooth!=null){active=JsonUtility.FromJson<Manifest>(smooth.text).clips[0];root="PracticalRetro/Essa225/";name="Essa225";}
                    }
                    var pages=new Texture2D[active.pages.Length];
                    for(int j=0;j<pages.Length;j++)
                    {
                        pages[j]=Resources.Load<Texture2D>(root+active.pages[j]);
                        if(pages[j]!=null) pages[j].filterMode=FilterMode.Bilinear;
                    }
                    var result=new Sprite[active.frames.Length]; var times=new float[result.Length];
                    for(int j=0;j<result.Length;j++)
                    {
                        var f=active.frames[j]; var r=f.rect;
                        if(r==null || r.Length!=4 || f.page<0 || f.page>=pages.Length || f.seconds<=0 || float.IsNaN(f.seconds))throw new InvalidOperationException("Invalid video frame");
                        if(pages[f.page]==null) throw new InvalidOperationException("Missing Essa222 atlas");
                        result[j]=Sprite.Create(pages[f.page],new Rect(r[0],r[1],r[2],r[3]),
                            new Vector2(manifest.pivot[0],manifest.pivot[1]),manifest.pixelsPerUnit,0,SpriteMeshType.FullRect);
                        result[j].name=$"{name}_{clip.action}_{j:00}"; times[j]=f.seconds;
                        created.Add(result[j]);
                    }
                    pending.Add(clip.action,result);pendingTimes.Add(clip.action,times);
                }
                foreach(var item in pending)Sprites.Add(item.Key,item.Value);
                foreach(var item in pendingTimes)Durations.Add(item.Key,item.Value);
                loaded=true;
                }
                catch(Exception e){foreach(var sprite in created)UnityEngine.Object.Destroy(sprite);Sprites.Clear();Durations.Clear();failed=true;Debug.LogError("FF_VIDEO: safe fallback: "+e.Message);return false;}
            }
            return Sprites.TryGetValue(action,out frames);
        }
        public static float[] Timing(string actor,string action)
        {
            return TryLoad(actor,action,out _) && Durations.TryGetValue(action,out var timing) ? timing : null;
        }
        public static float FrameStart(string actor,string action,int frame)
        {
            var times=Timing(actor,action);float result=0;
            if(times==null) return frame/12f;
            for(int i=0;i<Mathf.Min(frame,times.Length);i++) result+=times[i];
            return result;
        }
    }
}
