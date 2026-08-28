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

        private void Awake()
        {
            spriteRenderer = GetComponent<SpriteRenderer>();
            animator = GetComponent<SpriteStripAnimator>();
        }

        private void Update()
        {
            Vector2 move = input.ReadMove();
            Vector3 next = transform.position + new Vector3(move.x, move.y * 0.62f, 0f)
                * (Speed * Time.deltaTime);
            next.x = Mathf.Clamp(next.x, -8.2f, 8.2f);
            next.y = Mathf.Clamp(next.y, -3.6f, 0.5f);
            transform.position = next;

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
