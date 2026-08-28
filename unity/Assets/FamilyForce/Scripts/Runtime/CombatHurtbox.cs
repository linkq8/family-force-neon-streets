using UnityEngine;

namespace FamilyForce.Unity
{
    /// <summary>Stable world-space combat bounds independent of transparent sprite padding.</summary>
    public sealed class CombatHurtbox : MonoBehaviour
    {
        [SerializeField] private Vector2 size = new Vector2(0.72f, 1.28f);
        [SerializeField] private Vector2 offset = new Vector2(0f, 0.64f);

        public Rect Bounds => new Rect(
            transform.position.x + offset.x - size.x * 0.5f,
            transform.position.y + offset.y - size.y * 0.5f,
            size.x, size.y);

        public bool OverlapsAttack(Vector3 origin, bool facingRight, float reach, float height = 1.05f)
        {
            float centerX = origin.x + (facingRight ? reach * 0.55f : -reach * 0.55f);
            return Bounds.Overlaps(new Rect(centerX - reach * 0.5f, origin.y, reach, height));
        }
    }
}
