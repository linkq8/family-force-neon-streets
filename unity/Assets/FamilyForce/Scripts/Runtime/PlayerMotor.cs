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
        private float jumpTime;
        private Vector3 groundPosition;

        private void Awake()
        {
            spriteRenderer = GetComponent<SpriteRenderer>();
            animator = GetComponent<SpriteStripAnimator>();
            groundPosition = transform.position;
        }

        private void Update()
        {
            Vector2 move = input.ReadMove();
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

            if (input.PunchPressed())
                StartCoroutine(HitFlash());
        }

        private System.Collections.IEnumerator HitFlash()
        {
            spriteRenderer.color = new Color(1f, 0.72f, 0.34f, 1f);
            yield return new WaitForSecondsRealtime(0.08f);
            spriteRenderer.color = Color.white;
        }
    }
}
