using UnityEngine;
using UnityEngine.U2D;

namespace FamilyForce.Unity
{
    [RequireComponent(typeof(SpriteRenderer))]
    public sealed class WeaponPickup : MonoBehaviour
    {
        private SpriteRenderer spriteRenderer;
        private PlayerMotor owner;
        private Vector2 velocity;
        private bool thrown;
        private bool hitDuringThrow;

        public bool IsHeld => owner != null;
        public PlayerMotor Owner => owner;

        private void Awake()
        {
            spriteRenderer = GetComponent<SpriteRenderer>();
            SpriteAtlas atlas = Resources.Load<SpriteAtlas>("Atlases/FF_Stage1Props");
            spriteRenderer.sprite = atlas != null ? atlas.GetSprite("bat") : null;
            spriteRenderer.sortingOrder = 24;
        }

        public void ResetPickup(Vector3 position)
        {
            owner = null;
            thrown = false;
            hitDuringThrow = false;
            velocity = Vector2.zero;
            transform.position = position;
            transform.rotation = Quaternion.Euler(0f, 0f, -24f);
            gameObject.SetActive(true);
            TouchInputOverlay.SetWeaponHeld(false);
        }

        public bool TryPickup(PlayerMotor player)
        {
            if (player == null || owner != null || thrown
                || Vector2.Distance(transform.position, player.transform.position) > 1.65f)
                return false;
            owner = player;
            TouchInputOverlay.SetWeaponHeld(player.PlayerIndex == 0);
            return true;
        }

        public void Throw(PlayerMotor player)
        {
            if (owner != player)
                return;
            owner = null;
            thrown = true;
            hitDuringThrow = false;
            velocity = new Vector2(player.FacingRight ? 8.2f : -8.2f, 2.6f);
            TouchInputOverlay.SetWeaponHeld(false);
        }

        public void Consume()
        {
            owner = null;
            thrown = false;
            gameObject.SetActive(false);
            TouchInputOverlay.SetWeaponHeld(false);
        }

        private void Update()
        {
            if (owner != null)
            {
                transform.position = owner.transform.position
                    + new Vector3(owner.FacingRight ? 0.54f : -0.54f, 0.72f, -0.05f);
                transform.rotation = Quaternion.Euler(0f, 0f, owner.FacingRight ? -38f : 38f);
                spriteRenderer.flipX = !owner.FacingRight;
                return;
            }
            if (!thrown)
                return;
            velocity += Vector2.down * (7.5f * Time.deltaTime);
            transform.position += (Vector3)(velocity * Time.deltaTime);
            transform.Rotate(0f, 0f, velocity.x * -55f * Time.deltaTime);
            if (transform.position.y <= -2.25f)
            {
                transform.position = new Vector3(transform.position.x, -2.25f, transform.position.z);
                thrown = false;
                velocity = Vector2.zero;
                hitDuringThrow = false;
            }
        }

        public bool CanHitThrown(EnemyCombatant enemy) => thrown && !hitDuringThrow && enemy != null
            && enemy.IsAlive && Vector2.Distance(transform.position, enemy.transform.position) < 1.15f;

        public void MarkThrownHit() => hitDuringThrow = true;
    }
}
