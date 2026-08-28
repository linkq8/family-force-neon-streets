using UnityEngine;

namespace FamilyForce.Unity
{
    [RequireComponent(typeof(SpriteRenderer), typeof(SpriteStripAnimator))]
    public sealed class PlayerMotor : MonoBehaviour
    {
        private const float Speed = 4.2f;
        private readonly UnifiedInput input = new UnifiedInput();
        private SpriteRenderer spriteRenderer;
        private SpriteStripAnimator animator;
        private CombatDirector combat;
        private float jumpTime;
        private Vector3 groundPosition;
        private Sprite[] punchFrames;
        private Sprite[] kickFrames;
        private Sprite[] heavyFrames;
        private Sprite[] specialFrames;
        private Sprite[] linkFrames;
        private Sprite[] hurtFrames;

        private void Awake()
        {
            spriteRenderer = GetComponent<SpriteRenderer>();
            animator = GetComponent<SpriteStripAnimator>();
            groundPosition = transform.position;
        }

        public void Configure(CombatDirector director)
        {
            combat = director;
            punchFrames = CharacterAtlasCatalog.LoadClip(CharacterAtlasCatalog.Essa, "punch");
            kickFrames = CharacterAtlasCatalog.LoadClip(CharacterAtlasCatalog.Essa, "kick");
            heavyFrames = CharacterAtlasCatalog.LoadClip(CharacterAtlasCatalog.Essa, "heavy_punch");
            specialFrames = CharacterAtlasCatalog.LoadClip(CharacterAtlasCatalog.Essa, "special");
            linkFrames = CharacterAtlasCatalog.LoadClip(CharacterAtlasCatalog.Essa, "link");
            hurtFrames = CharacterAtlasCatalog.LoadClip(CharacterAtlasCatalog.Essa, "hurt");
        }

        public void PlayHurt() => animator.PlayOnce(hurtFrames);

        private void Update()
        {
            Vector2 move = input.ReadMove();
            if (animator.IsPlayingAction)
                move *= 0.28f;
            if (input.JumpPressed() && jumpTime <= 0f)
                jumpTime = 0.52f;
            Vector3 next = groundPosition + new Vector3(move.x, move.y * 0.62f, 0f)
                * (Speed * Time.deltaTime);
            next.x = Mathf.Clamp(next.x, -8.2f, 8.2f);
            next.y = Mathf.Clamp(next.y, -3.6f, 0.5f);
            groundPosition = next;

            float lift = 0f;
            if (jumpTime > 0f)
            {
                jumpTime = Mathf.Max(0f, jumpTime - Time.deltaTime);
                float progress = 1f - jumpTime / 0.52f;
                lift = Mathf.Sin(progress * Mathf.PI) * 0.72f;
            }
            transform.position = groundPosition + Vector3.up * lift;

            if (Mathf.Abs(move.x) > 0.01f)
                spriteRenderer.flipX = move.x < 0f;
            animator.SetMoving(move.sqrMagnitude > 0.01f);

            if (combat == null)
                return;
            if (input.TeamPressed())
                TryAction(CombatAction.Team, linkFrames);
            else if (input.GrabPressed())
                TryAction(CombatAction.Grab, heavyFrames);
            else if (input.SpecialPressed())
                TryAction(CombatAction.Special, specialFrames);
            else if (input.HeavyPressed())
                TryAction(CombatAction.Heavy, heavyFrames);
            else if (input.KickPressed())
                TryAction(CombatAction.Kick, kickFrames);
            else if (input.PunchPressed())
                TryAction(CombatAction.Punch, punchFrames);
        }

        private void TryAction(CombatAction action, Sprite[] frames)
        {
            if (combat.TryPlayerAction(action))
                animator.PlayOnce(frames);
        }
    }
}
