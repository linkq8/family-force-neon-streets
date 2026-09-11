using UnityEngine;
using System.Collections;

namespace FamilyForce.Unity
{
    [RequireComponent(typeof(SpriteRenderer), typeof(SpriteStripAnimator), typeof(CombatHurtbox))]
    public sealed class EnemyCombatant : MonoBehaviour
    {
        private CombatDirector director;
        private SpriteRenderer spriteRenderer;
        private SpriteStripAnimator animator;
        private Sprite[] attackFrames;
        private Sprite[] hurtFrames;
        private Sprite[] knockdownFrames;
        private float nextAttackTime;
        private float hurtLock;
        private float grabbedUntil;
        private float moveSpeed;
        private int attackDamage;
        private bool defeated;
        private int attackRevision;
        private bool attacking;

        public string DisplayName { get; private set; } = "GRUNT";
        public int MaxHealth { get; private set; } = 100;
        public int Health { get; private set; } = 100;
        public bool IsGrabbed => !defeated && grabbedUntil > Time.time;
        public bool IsAlive => !defeated;
        public PlayerMotor Grabber { get; private set; }
        public CombatHurtbox Hurtbox { get; private set; }

        private void Awake()
        {
            spriteRenderer = GetComponent<SpriteRenderer>();
            animator = GetComponent<SpriteStripAnimator>();
            Hurtbox = GetComponent<CombatHurtbox>();
        }

        public void Initialize(CombatDirector combatDirector)
        {
            director = combatDirector;
            gameObject.SetActive(false);
        }

        public void Spawn(string actor, string displayName, int maxHealth, float speed,
            int damage, Vector3 position, float scale)
        {
            DisplayName = displayName;
            StopAllCoroutines();attackRevision++;attacking=false;
            MaxHealth = maxHealth;
            moveSpeed = speed;
            attackDamage = damage;
            transform.localScale = Vector3.one * scale;
            animator.Initialize(CharacterAtlasCatalog.LoadClip(actor, "idle"),
                CharacterAtlasCatalog.LoadClip(actor, "walk"));
            attackFrames = CharacterAtlasCatalog.LoadClip(actor, "attack_1");
            hurtFrames = CharacterAtlasCatalog.LoadClip(actor, "hurt");
            knockdownFrames = CharacterAtlasCatalog.LoadClip(actor, "knockdown");
            Health = MaxHealth;
            defeated = false;
            Grabber = null;
            grabbedUntil = 0f;
            hurtLock = Time.time + 0.45f;
            nextAttackTime = Time.time + 1.15f;
            transform.position = position;
            spriteRenderer.color = Color.white;
            gameObject.SetActive(true);
            TouchInputOverlay.SetTeamReady(false);
        }

        public bool TryGrab(PlayerMotor player)
        {
            if (!IsAlive || player == null || DisplayName == "MARKET ENFORCER"
                || Vector2.Distance(transform.position, player.transform.position) > 1.55f)
                return false;
            Grabber = player;
            attackRevision++;attacking=false;
            grabbedUntil = Time.time + 2.8f;
            hurtLock = grabbedUntil;
            animator.PlayOnce(hurtFrames);
            TouchInputOverlay.SetTeamReady(true);
            return true;
        }

        public void TakeHit(int damage, float knockback, Transform attacker)
        {
            if (!IsAlive)
                return;
            Health = Mathf.Max(0, Health - damage);
            attackRevision++;attacking=false;
            grabbedUntil = 0f;
            Grabber = null;
            TouchInputOverlay.SetTeamReady(false);
            if (Health == 0)
            {
                defeated = true;
                animator.SetMoving(false);animator.PlayOnce(knockdownFrames,null,true);
                director.EnemyDefeated();
                return;
            }
            animator.PlayOnce(hurtFrames);
            hurtLock = Time.time + 0.25f;
            float direction = Mathf.Sign(transform.position.x - attacker.position.x);
            transform.position += Vector3.right * (direction * knockback);
        }

        public void ApplyTeamCombo()
        {
            if (!IsGrabbed)
                return;
            grabbedUntil = 0f;
            TouchInputOverlay.SetTeamReady(false);
            Transform attacker = Grabber != null ? Grabber.transform : transform;
            TakeHit(48, 1.15f, attacker);
        }

        private void Update()
        {
            spriteRenderer.sortingOrder=100-Mathf.RoundToInt(transform.position.y*10);
            if (director == null || !director.CombatActive || defeated)
                return;
            PlayerMotor target = director.ClosestActivePlayer(transform.position);
            if (target == null)
                return;
            if (IsGrabbed)
            {
                if (Grabber == null || !Grabber.gameObject.activeInHierarchy)
                {
                    grabbedUntil = 0f;
                    Grabber = null;
                    TouchInputOverlay.SetTeamReady(false);
                    return;
                }
                transform.position = Grabber.transform.position
                    + new Vector3(Grabber.FacingRight ? 0.88f : -0.88f, 0.03f, 0f);
                animator.SetMoving(false);
                return;
            }
            if (grabbedUntil > 0f)
            {
                grabbedUntil = 0f;
                Grabber = null;
                TouchInputOverlay.SetTeamReady(false);
            }
            if (Time.time < hurtLock || attacking)
                return;
            Vector2 delta = target.GroundPosition - transform.position;
            spriteRenderer.flipX = delta.x < 0f;
            if (Mathf.Abs(delta.x) > 1.15f || Mathf.Abs(delta.y) > 0.55f)
            {
                Vector2 direction = delta.normalized;
                transform.position += new Vector3(direction.x, direction.y * 0.7f, 0f)
                    * (moveSpeed * Time.deltaTime);
                animator.SetMoving(true);
                return;
            }
            animator.SetMoving(false);
            if (Time.time < nextAttackTime)
                return;
            nextAttackTime = Time.time + 1.35f;
            animator.PlayOnce(attackFrames);
            attacking=true;StartCoroutine(AttackContact(target,++attackRevision));
        }
        private IEnumerator AttackContact(PlayerMotor target,int revision)
        {
            float total=attackFrames.Length/12f;
            yield return new WaitForSeconds(total*.4f);
            if(revision!=attackRevision || defeated)yield break;
            Vector2 delta=target.GroundPosition-transform.position;
            if(director.CombatActive && target.gameObject.activeInHierarchy && !target.IsAirborne && Mathf.Abs(delta.x)<=1.15f && Mathf.Abs(delta.y)<=.55f)
                director.DamagePlayer(target,attackDamage);
            yield return new WaitForSeconds(total*.6f);
            if(revision==attackRevision)attacking=false;
        }
    }
}
