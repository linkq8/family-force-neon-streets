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
        private CombatAction? bufferedAction;
        private float bufferedUntil;
        private bool controlEnabled;

        public int PlayerIndex { get; private set; }
        public string ActorName { get; private set; } = CharacterAtlasCatalog.Essa;
        public string InputLabel => input.DeviceLabel;
        public bool HasGamepad => input.HasAssignedGamepad;
        public bool FacingRight => !spriteRenderer.flipX;

        private void Awake()
        {
            spriteRenderer = GetComponent<SpriteRenderer>();
            animator = GetComponent<SpriteStripAnimator>();
            groundPosition = transform.position;
        }

        public void Configure(CombatDirector director, string actor, int index, bool allowTouch)
        {
            combat = director;
            PlayerIndex = index;
            input = new UnifiedInput(index, allowTouch);
            SelectActor(actor);
            controlEnabled = true;
        }

        public void SelectActor(string actor)
        {
            ActorName = actor;
            Sprite[] idleFrames = CharacterAtlasCatalog.LoadClip(actor, "idle");
            Sprite[] walkFrames = CharacterAtlasCatalog.LoadClip(actor, "walk");
            animator.Initialize(idleFrames, walkFrames);
            punchFrames = CharacterAtlasCatalog.LoadClip(actor, "punch");
            kickFrames = CharacterAtlasCatalog.LoadClip(actor, "kick");
            heavyFrames = CharacterAtlasCatalog.LoadClip(actor, "heavy_punch");
            specialFrames = CharacterAtlasCatalog.LoadClip(actor, "special");
            linkFrames = CharacterAtlasCatalog.LoadClip(actor, "link");
            hurtFrames = CharacterAtlasCatalog.LoadClip(actor, "hurt");
            transform.localScale = Vector3.one * (actor == CharacterAtlasCatalog.Adam ? 2.65f : 3.45f);
        }

        public void SetControlEnabled(bool enabled)
        {
            controlEnabled = enabled;
            if (!enabled)
                animator.SetMoving(false);
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
            if (!controlEnabled)
                return;
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
            if (input.ThrowPressed())
                BufferAction(CombatAction.Throw);
            else if (input.WeaponPressed())
                BufferAction(CombatAction.Weapon);
            else if (input.TeamPressed())
                BufferAction(CombatAction.Team);
            else if (input.GrabPressed())
                BufferAction(CombatAction.Grab);
            else if (input.SpecialPressed())
                BufferAction(CombatAction.Special);
            else if (input.HeavyPressed())
                BufferAction(CombatAction.Heavy);
            else if (input.KickPressed())
                BufferAction(CombatAction.Kick);
            else if (input.PunchPressed())
                BufferAction(CombatAction.Punch);

            if (bufferedAction.HasValue && Time.unscaledTime <= bufferedUntil
                && TryAction(bufferedAction.Value))
                bufferedAction = null;
            else if (Time.unscaledTime > bufferedUntil)
                bufferedAction = null;
        }

        private void BufferAction(CombatAction action)
        {
            bufferedAction = action;
            bufferedUntil = Time.unscaledTime + 0.14f;
        }

        private bool TryAction(CombatAction action)
        {
            if (combat.TryPlayerAction(this, action))
            {
                Sprite[] frames = action switch
                {
                    CombatAction.Punch => punchFrames,
                    CombatAction.Kick => kickFrames,
                    CombatAction.Heavy => heavyFrames,
                    CombatAction.Special => specialFrames,
                    CombatAction.Grab => heavyFrames,
                    CombatAction.Team => linkFrames,
                    CombatAction.Weapon => heavyFrames,
                    CombatAction.Throw => kickFrames,
                    _ => punchFrames
                };
                animator.PlayOnce(frames);
                return true;
            }
            return false;
        }
    }
}
