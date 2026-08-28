using UnityEngine;

namespace FamilyForce.Unity
{
    [RequireComponent(typeof(SpriteRenderer), typeof(SpriteStripAnimator))]
    public sealed class EnemyCombatant : MonoBehaviour
    {
        public const int MaxHealth = 100;
        private const float MoveSpeed = 1.45f;

        private Transform target;
        private CombatDirector director;
        private SpriteRenderer spriteRenderer;
        private SpriteStripAnimator animator;
        private Sprite[] attackFrames;
        private Sprite[] hurtFrames;
        private Sprite[] knockdownFrames;
        private float nextAttackTime;
        private float hurtLock;
        private float grabbedUntil;
        private bool defeated;

        public int Health { get; private set; } = MaxHealth;
        public bool IsGrabbed => !defeated && grabbedUntil > Time.time;
        public bool IsAlive => !defeated;

        private void Awake()
        {
            spriteRenderer = GetComponent<SpriteRenderer>();
            animator = GetComponent<SpriteStripAnimator>();
        }

        public void Initialize(string actor, Transform player, CombatDirector combatDirector)
        {
            target = player;
            director = combatDirector;
            animator.Initialize(CharacterAtlasCatalog.LoadClip(actor, "idle"),
                CharacterAtlasCatalog.LoadClip(actor, "walk"));
            attackFrames = CharacterAtlasCatalog.LoadClip(actor, "attack_1");
            hurtFrames = CharacterAtlasCatalog.LoadClip(actor, "hurt");
            knockdownFrames = CharacterAtlasCatalog.LoadClip(actor, "knockdown");
            ResetEncounter();
        }

        public void ResetEncounter()
        {
            Health = MaxHealth;
            defeated = false;
            grabbedUntil = 0f;
            hurtLock = 0f;
            nextAttackTime = Time.time + 1.2f;
            transform.position = new Vector3(2.6f, -2.15f, 0f);
            spriteRenderer.color = Color.white;
            gameObject.SetActive(true);
            TouchInputOverlay.SetTeamReady(false);
        }

        public bool TryGrab()
        {
            if (!IsAlive || Vector2.Distance(transform.position, target.position) > 1.55f)
                return false;
            grabbedUntil = Time.time + 2.8f;
            hurtLock = grabbedUntil;
            animator.PlayOnce(hurtFrames);
            TouchInputOverlay.SetTeamReady(true);
            return true;
        }

        public void TakeHit(int damage, float knockback)
        {
            if (!IsAlive)
                return;
            Health = Mathf.Max(0, Health - damage);
            grabbedUntil = 0f;
            TouchInputOverlay.SetTeamReady(false);
            if (Health == 0)
            {
                defeated = true;
                animator.PlayOnce(knockdownFrames);
                director.EnemyDefeated();
                return;
            }

            animator.PlayOnce(hurtFrames);
            hurtLock = Time.time + 0.25f;
            float direction = Mathf.Sign(transform.position.x - target.position.x);
            transform.position += Vector3.right * (direction * knockback);
        }

        public void ApplyTeamCombo()
        {
            if (!IsGrabbed)
                return;
            grabbedUntil = 0f;
            TouchInputOverlay.SetTeamReady(false);
            TakeHit(48, 1.15f);
        }

        private void Update()
        {
            if (target == null || director == null || !director.CombatActive || defeated)
                return;

            if (IsGrabbed)
            {
                float side = spriteRenderer.flipX ? -1f : 1f;
                transform.position = target.position + new Vector3(side * 0.88f, 0.03f, 0f);
                animator.SetMoving(false);
                return;
            }
            if (grabbedUntil > 0f)
            {
                grabbedUntil = 0f;
                TouchInputOverlay.SetTeamReady(false);
            }
            if (Time.time < hurtLock)
                return;

            Vector2 delta = target.position - transform.position;
            spriteRenderer.flipX = delta.x < 0f;
            if (Mathf.Abs(delta.x) > 1.15f || Mathf.Abs(delta.y) > 0.55f)
            {
                Vector2 direction = delta.normalized;
                transform.position += new Vector3(direction.x, direction.y * 0.7f, 0f)
                    * (MoveSpeed * Time.deltaTime);
                animator.SetMoving(true);
                return;
            }

            animator.SetMoving(false);
            if (Time.time < nextAttackTime)
                return;
            nextAttackTime = Time.time + 1.35f;
            animator.PlayOnce(attackFrames);
            director.DamagePlayer(7);
        }
    }
}
