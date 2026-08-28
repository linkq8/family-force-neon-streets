using UnityEngine;

namespace FamilyForce.Unity
{
    [RequireComponent(typeof(SpriteRenderer), typeof(SpriteStripAnimator))]
    public sealed class PlayerMotor : MonoBehaviour
    {
        private const float Speed = 4.2f;
        private UnifiedInput input = new UnifiedInput();
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

        public int PlayerIndex { get; private set; }
        public string ActorName { get; private set; } = CharacterAtlasCatalog.Essa;
        public string InputLabel => input.DeviceLabel;
        public bool HasGamepad => input.HasAssignedGamepad;

        private void Awake()
        {
            spriteRenderer = GetComponent<SpriteRenderer>();
            animator = GetComponent<SpriteStripAnimator>();
            groundPosition = transform.position;
        }

        public void Configure(CombatDirector director, string actor, int index, bool allowTouch)
        {
            combat = director;
            ActorName = actor;
            PlayerIndex = index;
            input = new UnifiedInput(index, allowTouch);
            punchFrames = CharacterAtlasCatalog.LoadClip(actor, "punch");
            kickFrames = CharacterAtlasCatalog.LoadClip(actor, "kick");
            heavyFrames = CharacterAtlasCatalog.LoadClip(actor, "heavy_punch");
            specialFrames = CharacterAtlasCatalog.LoadClip(actor, "special");
            linkFrames = CharacterAtlasCatalog.LoadClip(actor, "link");
            hurtFrames = CharacterAtlasCatalog.LoadClip(actor, "hurt");
        }

        public void PlayHurt() => animator.PlayOnce(hurtFrames);
        public void PlayTeamAction() => animator.PlayOnce(linkFrames);

        public void ResetPosition(Vector3 position)
        {
            groundPosition = position;
            jumpTime = 0f;
            transform.position = position;
        }

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
            if (combat.TryPlayerAction(this, action))
                animator.PlayOnce(frames);
        }
    }
}
