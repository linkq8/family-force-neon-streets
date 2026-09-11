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
        private bool jumping;
        private Vector3 bodyScale;

        public int PlayerIndex { get; private set; }
        public string ActorName { get; private set; } = CharacterAtlasCatalog.Essa;
        public string InputLabel => input.DeviceLabel;
        public bool HasGamepad => input.HasAssignedGamepad;
        public bool FacingRight => !spriteRenderer.flipX;
        public Vector3 GroundPosition => groundPosition;
        public bool IsAirborne => jumpTime > 0f;
        public int ActionRevision { get; private set; }

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
            ActionRevision++;
            ActorName = actor;
            Sprite[] idleFrames = CharacterAtlasCatalog.LoadClip(actor, "idle");
            Sprite[] walkFrames = CharacterAtlasCatalog.LoadClip(actor, "walk");
            animator.Initialize(idleFrames, walkFrames, VideoEssaClips.Timing(actor,"idle"), VideoEssaClips.Timing(actor,"walk"));
            punchFrames = CharacterAtlasCatalog.LoadClip(actor, "punch");
            kickFrames = CharacterAtlasCatalog.LoadClip(actor, "kick");
            heavyFrames = CharacterAtlasCatalog.LoadClip(actor, "heavy_punch");
            specialFrames = CharacterAtlasCatalog.LoadClip(actor, "special");
            linkFrames = CharacterAtlasCatalog.LoadClip(actor, "link");
            hurtFrames = CharacterAtlasCatalog.LoadClip(actor, "hurt");
            transform.localScale = Vector3.one * (actor == CharacterAtlasCatalog.Adam ? 2.65f : 3.45f);
            bodyScale=transform.localScale;
        }

        public void SetControlEnabled(bool enabled)
        {
            controlEnabled = enabled;
            if (!enabled)
            {
                bufferedAction=null;
                EndJump();
                animator.SetMoving(false);
            }
        }

        public void PlayHurt() { bufferedAction=null;EndJump();ActionRevision++; animator.PlayOnce(hurtFrames); }
        public void PlayTeamAction() { ActionRevision++; animator.PlayOnce(linkFrames); }
        public float PlayKnockdown()
        {
            ActionRevision++;
            var frames=CharacterAtlasCatalog.LoadClip(ActorName,"knockdown");
            var timing=ActionTiming.Durations(ActorName,"knockdown",frames.Length);
            animator.PlayOnce(frames,timing,true);
            float total=0; if(timing!=null) foreach(float t in timing) total+=t;
            return timing!=null ? total : frames.Length/12f;
        }

        public void ResetPosition(Vector3 position)
        {
            groundPosition = position;
            bufferedAction=null;EndJump();
            jumpTime = 0f;
            transform.position = position;
            ActionRevision++; animator.StopAction();
        }

        private void Update()
        {
            if (!controlEnabled)
                return;
            Vector2 move = input.ReadMove();
            move = SmoothWalkInput(move);
            // Intended speed before action slowdown and the scene's Y perspective.
            float gaitRate = Mathf.Lerp(1.2f,1.5f,Mathf.InverseLerp(.8f,1f,move.magnitude));
            if (animator.IsPlayingAction)
                move *= 0.28f;
            if (input.JumpPressed() && jumpTime <= 0f && !animator.IsPlayingAction)
            {
                jumpTime = 0.52f;jumping=true;ActionRevision++;
                var poses=CharacterAtlasCatalog.LoadClip(ActorName,"jump");
                if(poses.Length>0){var durations=new float[poses.Length];for(int i=0;i<durations.Length;i++)durations[i]=.52f/durations.Length;animator.PlayOnce(poses,durations);}
            }
            Vector3 oldGround = groundPosition;
            Vector3 next = groundPosition + new Vector3(move.x, move.y * 0.62f, 0f)
                * ((ActorName == CharacterAtlasCatalog.Essa ? 4.8f : Speed) * Time.deltaTime);
            next.x = Mathf.Clamp(next.x, -8.2f, 8.2f);
            next.y = Mathf.Clamp(next.y, -3.6f, 0.5f);
            groundPosition = next;

            float lift = 0f;
            if (jumpTime > 0f)
            {
                jumpTime = Mathf.Max(0f, jumpTime - Time.deltaTime);
                float progress = 1f - jumpTime / 0.52f;
                lift = Mathf.Sin(progress * Mathf.PI) * 0.72f;
                // Procedural takeoff/air/landing, not newly authored art.
                float stretch=Mathf.Sin(progress*Mathf.PI)*.07f;
                transform.localScale=new Vector3(bodyScale.x*(1-stretch),bodyScale.y*(1+stretch),bodyScale.z);
                transform.rotation=Quaternion.Euler(0,0,(FacingRight?-1:1)*6*Mathf.Sin(progress*Mathf.PI));
            }
            else if(jumping)EndJump();
            transform.position = groundPosition + Vector3.up * lift;
            spriteRenderer.sortingOrder=100-Mathf.RoundToInt(groundPosition.y*10);

            if (Mathf.Abs(move.x) > 0.01f)
                spriteRenderer.flipX = move.x < 0f;
            bool displaced = (groundPosition-oldGround).sqrMagnitude > .00000001f;
            animator.SetMoving(displaced && move.sqrMagnitude > 0.01f);
            if (displaced)
                animator.SetWalkRate(gaitRate);

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

            if (bufferedAction.HasValue && Time.time <= bufferedUntil
                && TryAction(bufferedAction.Value))
                bufferedAction = null;
            else if (Time.time > bufferedUntil)
                bufferedAction = null;
        }

        private void BufferAction(CombatAction action)
        {
            bufferedAction = action;
            bufferedUntil = Time.time + ActionTiming.BufferWindow(animator.RemainingActionTime);
        }
        private void EndJump()
        {jumpTime=0;jumping=false;transform.rotation=Quaternion.identity;if(bodyScale!=Vector3.zero)transform.localScale=bodyScale;transform.position=groundPosition;}

        public static Vector2 SmoothWalkInput(Vector2 move)
        {
            float magnitude=move.magnitude;
            if(magnitude<=.22f)return Vector2.zero;
            // Remap displacement AND cadence, rather than speeding feet in place.
            return move.normalized*Mathf.Lerp(.8f,1f,Mathf.InverseLerp(.22f,1f,magnitude));
        }

        private bool TryAction(CombatAction action)
        {
            if (animator.IsPlayingAction || IsAirborne) return false;
            if (combat.TryPlayerAction(this, action))
            {
                ActionRevision++;
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
                string clip=action==CombatAction.Punch?"punch":action==CombatAction.Kick||action==CombatAction.Throw?"kick":"other";
                float[] timing = ActionTiming.Durations(ActorName,clip,frames.Length);
                animator.PlayOnce(frames, timing);
                return true;
            }
            return false;
        }
    }
}
