using UnityEngine;
namespace FamilyForce.Unity
{
    // The visual player and hit scheduling consume exactly the same durations.
    public static class ActionTiming
    {
        public static float Rate(string action) => action=="punch"?1.4f:action=="knockdown"?1.8f:1f;
        public static float[] Durations(string actor,string action,int frames)
        {
            var source=VideoEssaClips.Timing(actor,action);var result=new float[frames];
            for(int i=0;i<frames;i++)result[i]=Mathf.Max(.016f,(source!=null&&i<source.Length?source[i]:1f/12)/Rate(action));
            return result;
        }
        public static float Start(string actor,string action,int frames,int contact)
        {var times=Durations(actor,action,frames);float sum=0;for(int i=0;i<Mathf.Min(contact,times.Length);i++)sum+=times[i];return sum;}
        public static float BufferWindow(float remaining) => Mathf.Clamp(remaining+.12f,.16f,1.2f);
    }
}
