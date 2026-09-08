using System;

namespace FamilyForce.Unity
{
    [Serializable]
    public sealed class CharacterArtManifest
    {
        public string contractVersion;
        public string status;
        public CharacterArtActor actor;
        public CharacterArtAction[] actions;
    }

    [Serializable]
    public sealed class CharacterArtActor
    {
        public string id;
        public string @class;
        public string profileVersion;
    }

    [Serializable]
    public sealed class CharacterArtAction
    {
        public string id;
        public float playbackFps;
        public bool loop;
        public CharacterArtFrame[] frames;
    }

    [Serializable]
    public sealed class CharacterArtFrame
    {
        public int sequence;
        public string runtime;
        public string runtimeSha256;
    }

    [Serializable]
    public sealed class CharacterArtApproval
    {
        public string status;
        public string actor;
        public string packageSha256;
        public string manifestSha256;
    }
}
