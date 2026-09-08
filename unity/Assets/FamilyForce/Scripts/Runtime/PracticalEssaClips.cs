using UnityEngine;
using System.Collections.Generic;

namespace FamilyForce.Unity
{
    /// <summary>
    /// Request198 sparse retro integration:12 walk drawings and8 combat keys.
    /// Repeated indices below are timed holds, not additional authored drawings.
    /// The source has extracted alpha, not native-generation transparency.
    /// </summary>
    public static class PracticalEssaClips
    {
        private static Sprite[] walk;
        private static Sprite[] idle;
        private static Sprite[] combat;
        private static readonly Dictionary<string, Sprite[]> Clips = new Dictionary<string, Sprite[]>();

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.SubsystemRegistration)]
        private static void ResetCache()
        {
            if (walk != null)
                foreach (Sprite sprite in walk)
                    if (sprite != null) Object.Destroy(sprite);
            walk = null;
            idle = null;
            if (combat != null)
                foreach (Sprite sprite in combat)
                    if (sprite != null) Object.Destroy(sprite);
            combat = null;
            Clips.Clear();
        }

        public static bool TryLoad(string actor, string action, out Sprite[] frames)
        {
            frames = null;
            if (actor != CharacterAtlasCatalog.Essa || string.IsNullOrEmpty(action))
                return false;
            if (walk == null)
            {
                Texture2D page = Resources.Load<Texture2D>("PracticalRetro/Essa198/Essa_walk");
                if (page == null || page.width != 1536 || page.height != 1152)
                    return false;
                Texture2D combatPage = Resources.Load<Texture2D>("PracticalRetro/Essa198/Essa_combat");
                if (combatPage == null || combatPage.width != 2048 || combatPage.height != 1024)
                    return false;
                walk = new Sprite[12];
                for (int i = 0; i < walk.Length; i++)
                {
                    Rect rect = new Rect((i % 4) * 384, (2 - i / 4) * 384, 384, 384);
                    walk[i] = Sprite.Create(page, rect, new Vector2(0.5f, 24f / 384f),
                        384f, 0, SpriteMeshType.FullRect);
                    walk[i].name = $"Essa198_walk_{i:00}";
                }
                combat = new Sprite[8];
                string[] names = { "guard", "windup", "punch", "kick", "uppercut", "palm", "hurt", "down" };
                for (int i = 0; i < combat.Length; i++)
                {
                    combat[i] = Sprite.Create(combatPage,
                        new Rect((i % 4) * 512, (1 - i / 4) * 512, 512, 512),
                        new Vector2(224f / 512f, 24f / 512f), 384f, 0, SpriteMeshType.FullRect);
                    combat[i].name = "Essa198_" + names[i];
                }
                idle = new[] { combat[0] };
                Clips["idle"] = idle;
                // Keep opposing lead-leg contact groups in opposite half-cycles.
                // This reorders source poses; it does not invent missing inbetweens.
                int[] order = { 0,1,7,4,3,5,2,6,8,10,11,9 };
                var orderedWalk = new Sprite[order.Length];
                for (int i = 0; i < order.Length; i++) orderedWalk[i] = walk[order[i]];
                Clips["walk"] = orderedWalk;
                Clips["punch"] = Hold(1,2,2,0);
                Clips["kick"] = Hold(0,3,3,0);
                Clips["heavy_punch"] = Hold(1,4,4,4,0,0);
                Clips["heavy_kick"] = Hold(1,3,3,3,0,0);
                Clips["special"] = Hold(1,5,5,5,0,0);
                Clips["link"] = Hold(1,5,5,5,0,0);
                Clips["hurt"] = Hold(6,6,0);
                Clips["jump"] = idle; // Vertical arc is authored by PlayerMotor.
                Clips["knockdown"] = Hold(6,7,7,7,7,7);
            }
            return Clips.TryGetValue(action, out frames);
        }

        private static Sprite[] Hold(params int[] indices)
        {
            var result = new Sprite[indices.Length];
            for (int i = 0; i < result.Length; i++) result[i] = combat[indices[i]];
            return result;
        }
    }
}
