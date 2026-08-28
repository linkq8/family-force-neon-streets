using UnityEngine;

namespace FamilyForce.Unity
{
    /// <summary>Deterministic 12-image strip player, independent of render FPS.</summary>
    [RequireComponent(typeof(SpriteRenderer))]
    public sealed class SpriteStripAnimator : MonoBehaviour
    {
        private const int FrameCount = 12;
        private const float AnimationFps = 12f;

        private SpriteRenderer target;
        private Sprite[] idleFrames;
        private Sprite[] walkFrames;
        private float accumulator;
        private int frame;
        private bool moving;

        public void Initialize(Texture2D idle, Texture2D walk)
        {
            target = GetComponent<SpriteRenderer>();
            if (idle == null)
            {
                Debug.LogError("FF_UNITY: missing parent_idle Resources texture");
                return;
            }
            idleFrames = Slice(idle);
            walkFrames = Slice(walk != null ? walk : idle);
            frame = 0;
            accumulator = 0f;
            ApplyFrame();
            Debug.Log($"FF_UNITY: sprite initialized texture={idle.width}x{idle.height} " +
                $"frames={idleFrames?.Length ?? 0} sprite={(target.sprite != null)}");
        }

        public void SetMoving(bool value)
        {
            if (moving == value)
                return;
            moving = value;
            frame = 0;
            accumulator = 0f;
            ApplyFrame();
        }

        private void Update()
        {
            accumulator += Time.unscaledDeltaTime * AnimationFps;
            while (accumulator >= 1f)
            {
                accumulator -= 1f;
                frame = (frame + 1) % FrameCount;
                ApplyFrame();
            }
        }

        private void ApplyFrame()
        {
            Sprite[] frames = moving ? walkFrames : idleFrames;
            if (target != null && frames != null && frames.Length == FrameCount)
                target.sprite = frames[frame];
        }

        private static Sprite[] Slice(Texture2D texture)
        {
            if (texture == null || texture.width % FrameCount != 0)
                return null;
            int width = texture.width / FrameCount;
            var sprites = new Sprite[FrameCount];
            for (int index = 0; index < FrameCount; index++)
            {
                var rect = new Rect(index * width, 0, width, texture.height);
                sprites[index] = Sprite.Create(texture, rect, new Vector2(0.5f, 0.04f),
                    100f, 0, SpriteMeshType.FullRect);
                sprites[index].name = $"frame_{index:00}";
            }
            return sprites;
        }
    }
}
