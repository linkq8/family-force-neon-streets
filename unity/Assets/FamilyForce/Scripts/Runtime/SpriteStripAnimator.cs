using UnityEngine;

namespace FamilyForce.Unity
{
    /// <summary>Deterministic Sprite Atlas clip player, independent of render FPS.</summary>
    [RequireComponent(typeof(SpriteRenderer))]
    public sealed class SpriteStripAnimator : MonoBehaviour
    {
        private const float AnimationFps = 12f;

        private SpriteRenderer target;
        private Sprite[] idleFrames;
        private Sprite[] walkFrames;
        private float accumulator;
        private int frame;
        private bool moving;

        public void Initialize(Sprite[] idle, Sprite[] walk)
        {
            target = GetComponent<SpriteRenderer>();
            if (idle == null || idle.Length == 0)
            {
                Debug.LogError("FF_UNITY: missing idle clip in Sprite Atlas");
                return;
            }
            idleFrames = idle;
            walkFrames = walk != null && walk.Length > 0 ? walk : idle;
            frame = 0;
            accumulator = 0f;
            ApplyFrame();
            Debug.Log($"FF_UNITY: atlas sprite initialized idle={idleFrames.Length} " +
                $"walk={walkFrames.Length} sprite={(target.sprite != null)}");
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
                Sprite[] frames = moving ? walkFrames : idleFrames;
                if (frames == null || frames.Length == 0)
                    continue;
                frame = (frame + 1) % frames.Length;
                ApplyFrame();
            }
        }

        private void ApplyFrame()
        {
            Sprite[] frames = moving ? walkFrames : idleFrames;
            if (target != null && frames != null && frames.Length > 0)
                target.sprite = frames[Mathf.Clamp(frame, 0, frames.Length - 1)];
        }
    }
}
