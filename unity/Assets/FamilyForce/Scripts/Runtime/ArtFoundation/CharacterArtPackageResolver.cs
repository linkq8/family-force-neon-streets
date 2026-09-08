using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.U2D;

namespace FamilyForce.Unity
{
    /// <summary>
    /// Enables a candidate only as a complete actor package. A missing action,
    /// frame, approval, or Atlas atomically returns the whole actor to legacy art.
    /// </summary>
    public static class CharacterArtPackageResolver
    {
        private sealed class ResolvedPackage
        {
            public CharacterArtManifest Manifest;
            public SpriteAtlas Atlas;
            public Dictionary<string, Sprite[]> Clips;
        }

        private static readonly Dictionary<string, ResolvedPackage> Cache = new();
        private static readonly HashSet<string> Failed = new();

        private static readonly string[] HeroActions =
        {
            "idle", "walk", "punch", "kick", "heavy_punch", "heavy_kick",
            "jump", "special", "link", "hurt", "knockdown"
        };

        private static readonly string[] EnemyActions =
        {
            "idle", "walk", "attack_1", "attack_2", "hurt", "knockdown"
        };

        public static bool TryLoadClip(string actor, string action, out Sprite[] frames)
        {
            frames = Array.Empty<Sprite>();
            if (!TryResolve(actor, out ResolvedPackage package))
                return false;
            if (!package.Clips.TryGetValue(action, out frames) || frames.Length < 12)
            {
                Disable(actor, $"candidate action unavailable: {action}");
                frames = Array.Empty<Sprite>();
                return false;
            }
            return true;
        }

        public static bool IsCandidateActive(string actor) => TryResolve(actor, out _);

        public static void InvalidateAll()
        {
            Cache.Clear();
            Failed.Clear();
        }

        private static bool TryResolve(string actor, out ResolvedPackage package)
        {
            if (Cache.TryGetValue(actor, out package))
                return true;
            if (Failed.Contains(actor))
                return false;

            TextAsset manifestAsset = Resources.Load<TextAsset>($"ArtFoundation/Manifests/{actor}");
            TextAsset approvalAsset = Resources.Load<TextAsset>($"ArtFoundation/Approvals/{actor}");
            SpriteAtlas atlas = Resources.Load<SpriteAtlas>($"ArtFoundation/Atlases/FFAF_{actor}");
            if (manifestAsset == null || approvalAsset == null || atlas == null)
                return Fail(actor, "candidate package is incomplete", out package);

            CharacterArtManifest manifest;
            CharacterArtApproval approval;
            try
            {
                manifest = JsonUtility.FromJson<CharacterArtManifest>(manifestAsset.text);
                approval = JsonUtility.FromJson<CharacterArtApproval>(approvalAsset.text);
            }
            catch (Exception exception)
            {
                return Fail(actor, $"candidate JSON error: {exception.Message}", out package);
            }

            if (manifest?.actor == null || manifest.actor.id != actor
                || manifest.contractVersion != "ff-art-1.0.0" || manifest.status != "ready"
                || approval == null || approval.actor != actor || approval.status != "approved")
                return Fail(actor, "candidate is not hash-approved and ready", out package);

            string[] required = actor == CharacterAtlasCatalog.Essa || actor == CharacterAtlasCatalog.Adam
                ? HeroActions : EnemyActions;
            var clips = new Dictionary<string, Sprite[]>(StringComparer.Ordinal);
            foreach (string requiredAction in required)
            {
                CharacterArtAction action = Array.Find(manifest.actions,
                    item => item != null && item.id == requiredAction);
                if (action?.frames == null || action.frames.Length < 12 || action.playbackFps < 12f)
                    return Fail(actor, $"required action is incomplete: {requiredAction}", out package);
                var sprites = new Sprite[action.frames.Length];
                for (int index = 0; index < sprites.Length; index++)
                {
                    sprites[index] = atlas.GetSprite($"{actor}_{requiredAction}_{index:00}");
                    if (sprites[index] == null)
                        return Fail(actor, $"candidate sprite is missing: {requiredAction}/{index:00}", out package);
                }
                clips[requiredAction] = sprites;
            }

            package = new ResolvedPackage { Manifest = manifest, Atlas = atlas, Clips = clips };
            Cache[actor] = package;
            Debug.Log($"FF_ART: activated complete approved candidate package actor={actor}");
            return true;
        }

        private static bool Fail(string actor, string reason, out ResolvedPackage package)
        {
            package = null;
            Failed.Add(actor);
            Debug.Log($"FF_ART: fallback actor={actor} reason={reason}");
            return false;
        }

        private static void Disable(string actor, string reason)
        {
            Cache.Remove(actor);
            Failed.Add(actor);
            Debug.LogError($"FF_ART: disabled candidate actor={actor} reason={reason}");
        }
    }
}
