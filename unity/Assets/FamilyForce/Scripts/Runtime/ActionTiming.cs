using UnityEngine;
namespace FamilyForce.Unity
{
    // The visual player and hit scheduling consume exactly the same durations.
    public static class ActionTiming
    {
        public static float Rate(string action) => action=="punch"?1.4f:action=="knockdown"?1.8f:1f;
        public static float[] Durations(string actor,string action,int frames)
        {
            // Explicit arcade budgets, not source-video playback speed.
            if(action=="punch" && actor==CharacterAtlasCatalog.Essa && frames==14)
            {
                var punch=new float[14];
                for(int i=0;i<14;i++)punch[i]=Mathf.Max(.016f,i<5?.08f/5:i<8?.07f/3:.13f/6);
                return punch; // contacts at .080/.150; ready again at .280 seconds.
            }
            if(action=="punch" || action=="kick" || action=="heavy_punch" || action=="special")
            {
                float total=action=="punch"?.22f:action=="kick"?.32f:action=="heavy_punch"?.42f:.50f;
                int contact=Mathf.Clamp(action=="kick" && actor==CharacterAtlasCatalog.Essa?6:frames/3,1,Mathf.Max(1,frames-1));
                float startup=action=="punch"?4f/60:action=="kick"?.10f:.14f;
                var timing=new float[frames];
                for(int i=0;i<frames;i++)timing[i]=Mathf.Max(.016f,i<contact?startup/contact:(total-startup)/(frames-contact));
                return timing;
            }
            var source=VideoEssaClips.Timing(actor,action);var result=new float[frames];
            for(int i=0;i<frames;i++)result[i]=Mathf.Max(.016f,(source!=null&&i<source.Length?source[i]:1f/12)/Rate(action));
            return result;
        }
        public static string Clip(CombatAction action)=>action==CombatAction.Punch?"punch":action==CombatAction.Kick||action==CombatAction.Throw?"kick":action==CombatAction.Heavy||action==CombatAction.Weapon||action==CombatAction.Grab?"heavy_punch":action==CombatAction.Special?"special":"other";
        public static float Start(string actor,string action,int frames,int contact)
        {var times=Durations(actor,action,frames);float sum=0;for(int i=0;i<Mathf.Min(contact,times.Length);i++)sum+=times[i];return sum;}
        public static float BufferWindow(float remaining) => Mathf.Clamp(remaining+.12f,.16f,1.2f);
    }
}
