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
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.SubsystemRegistration)]
        private static void Reset()
        {
            foreach(var frames in Sprites.Values) foreach(var s in frames) if(s!=null) UnityEngine.Object.Destroy(s);
            Sprites.Clear(); Durations.Clear(); loaded=false;
        }
        public static bool TryLoad(string actor,string action,out Sprite[] frames)
        {
            frames=null;
            if(actor!=CharacterAtlasCatalog.Essa) return false;
            if(!loaded)
            {
                loaded=true;
                var json=Resources.Load<TextAsset>("PracticalRetro/Essa222/clips");
                if(json==null) return false;
                var manifest=JsonUtility.FromJson<Manifest>(json.text);
                foreach(var clip in manifest.clips)
                {
                    var pages=new Texture2D[clip.pages.Length];
                    for(int j=0;j<pages.Length;j++)
                    {
                        pages[j]=Resources.Load<Texture2D>("PracticalRetro/Essa222/"+clip.pages[j]);
                        if(pages[j]!=null) pages[j].filterMode=FilterMode.Bilinear;
                    }
                    var result=new Sprite[clip.frames.Length]; var times=new float[result.Length];
                    for(int j=0;j<result.Length;j++)
                    {
                        var f=clip.frames[j]; var r=f.rect;
                        if(pages[f.page]==null) throw new InvalidOperationException("Missing Essa222 atlas");
                        result[j]=Sprite.Create(pages[f.page],new Rect(r[0],r[1],r[2],r[3]),
                            new Vector2(manifest.pivot[0],manifest.pivot[1]),manifest.pixelsPerUnit,0,SpriteMeshType.FullRect);
                        result[j].name=$"Essa222_{clip.action}_{j:00}"; times[j]=f.seconds;
                    }
                    Sprites.Add(clip.action,result);Durations.Add(clip.action,times);
                }
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
