using System;
using UnityEngine;
using UnityEngine.U2D;

namespace FamilyForce.Unity
{
    /// <summary>Single source of truth for character atlases and authored clip sizes.</summary>
    public static class CharacterAtlasCatalog
    {
        public const string Essa = "Essa";
        public const string Adam = "Adam";
        public const string Grunt = "Grunt";
        public const string Skater = "Skater";
        public const string LanternCourier = "LanternCourier";
        public const string MarketEnforcer = "MarketEnforcer";
        public const string Keeper7 = "Keeper7";

        public static readonly string[] StageOneEnemies =
        {
            Grunt, Skater, LanternCourier, MarketEnforcer, Keeper7
        };

        public static SpriteAtlas Load(string actor)
        {
            if (string.IsNullOrWhiteSpace(actor))
                return null;
            return Resources.Load<SpriteAtlas>($"Atlases/FF_{actor}");
        }

        public static Sprite[] LoadClip(string actor, string action)
        {
            SpriteAtlas atlas = Load(actor);
            if (atlas == null)
            {
                Debug.LogError($"FF_UNITY: missing Sprite Atlas for {actor}");
                return Array.Empty<Sprite>();
            }

            int count = FrameCount(actor, action);
            var frames = new Sprite[count];
            for (int index = 0; index < count; index++)
            {
                string name = $"{actor}_{action}_{index:00}";
                frames[index] = atlas.GetSprite(name);
                if (frames[index] == null)
                {
                    Debug.LogError($"FF_UNITY: missing atlas sprite {name}");
                    return Array.Empty<Sprite>();
                }
            }
            return frames;
        }

        public static int FrameCount(string actor, string action)
        {
            if (actor == Essa)
                return 12;
            if (actor == Adam)
                return 8;
            if (actor == MarketEnforcer && action == "walk")
                return 12;
            return 6;
        }
    }
}
