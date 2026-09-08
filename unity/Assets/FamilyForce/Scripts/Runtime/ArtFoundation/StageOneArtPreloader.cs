using System.Collections;
using UnityEngine;

namespace FamilyForce.Unity
{
    /// <summary>Warms only the actors used by Stage 1 before combat can spawn them.</summary>
    public sealed class StageOneArtPreloader : MonoBehaviour
    {
        public bool IsReady { get; private set; }

        private IEnumerator Start()
        {
            string[] actors =
            {
                CharacterAtlasCatalog.Essa, CharacterAtlasCatalog.Adam,
                CharacterAtlasCatalog.Grunt, CharacterAtlasCatalog.MarketEnforcer
            };
            foreach (string actor in actors)
            {
                CharacterAtlasCatalog.Load(actor);
                CharacterArtPackageResolver.IsCandidateActive(actor);
                yield return null;
            }
            IsReady = true;
            Debug.Log("FF_ART: Stage 1 actor atlases warmed without first-spawn decode");
        }
    }
}
