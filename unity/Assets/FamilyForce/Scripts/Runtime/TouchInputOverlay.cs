using UnityEngine;

namespace FamilyForce.Unity
{
    /// <summary>
    /// Allocation-free mobile touch bridge. It feeds the same UnifiedInput
    /// surface used by controllers and TV remotes, so gameplay never forks by
    /// device type. Coordinates use the prototype's 1920x1080 reference space.
    /// </summary>
    [DefaultExecutionOrder(-200)]
    public sealed class TouchInputOverlay : MonoBehaviour
    {
        private const float ReferenceWidth = 1920f;
        private const float ReferenceHeight = 1080f;
        private const float StickRadius = 154f;
        private static readonly Vector2 StickCenter = new Vector2(250f, 840f);
        private const float ActionRadius = 88f;
        private static readonly Vector2 GrabCenter = new Vector2(1250f, 730f);
        private static readonly Vector2 HeavyCenter = new Vector2(1430f, 730f);
        private static readonly Vector2 SpecialCenter = new Vector2(1610f, 730f);
        private static readonly Vector2 TeamCenter = new Vector2(1790f, 730f);
        private static readonly Vector2 JumpCenter = new Vector2(1250f, 930f);
        private static readonly Vector2 KickCenter = new Vector2(1430f, 930f);
        private static readonly Vector2 PunchCenter = new Vector2(1610f, 930f);
        private static readonly Vector2 MenuCenter = new Vector2(1805f, 130f);
        private static readonly Vector2[] beganPositions = new Vector2[10];

        private static int beganCount;
        private static int punchFrame = -1;
        private static int jumpFrame = -1;
        private static int kickFrame = -1;
        private static int heavyFrame = -1;
        private static int specialFrame = -1;
        private static int grabFrame = -1;
        private static int teamFrame = -1;
        private static int cancelFrame = -1;
        private static int confirmFrame = -1;
        private static bool gameplayActive;
        private static bool touchAvailable;
        private static Vector2 move;
        private static bool teamReady;

        public static Vector2 Move => gameplayActive && touchAvailable ? move : Vector2.zero;
        public static bool PunchPressedThisFrame => punchFrame == Time.frameCount;
        public static bool JumpPressedThisFrame => jumpFrame == Time.frameCount;
        public static bool KickPressedThisFrame => kickFrame == Time.frameCount;
        public static bool HeavyPressedThisFrame => heavyFrame == Time.frameCount;
        public static bool SpecialPressedThisFrame => specialFrame == Time.frameCount;
        public static bool GrabPressedThisFrame => grabFrame == Time.frameCount;
        public static bool TeamPressedThisFrame => teamFrame == Time.frameCount;
        public static bool CancelPressedThisFrame => cancelFrame == Time.frameCount;
        public static bool ConfirmPressedThisFrame => confirmFrame == Time.frameCount;
        public static bool IsAvailable => touchAvailable;

        public static void SetTeamReady(bool ready) => teamReady = ready;

        public static void SetGameplayActive(bool active)
        {
            gameplayActive = active;
            if (!active)
                move = Vector2.zero;
        }

        public static bool BeganInside(Rect referenceRect)
        {
            if (!touchAvailable)
                return false;
            for (int index = 0; index < beganCount; index++)
            {
                if (referenceRect.Contains(beganPositions[index]))
                    return true;
            }
            return false;
        }

        private void Awake()
        {
            touchAvailable = Input.touchSupported && SystemInfo.deviceType != DeviceType.Console;
            Input.multiTouchEnabled = true;
            Input.simulateMouseWithTouches = false;
        }

        private void Update()
        {
            beganCount = 0;
            move = Vector2.zero;
            if (!touchAvailable)
                return;

            for (int index = 0; index < Input.touchCount; index++)
            {
                Touch touch = Input.GetTouch(index);
                Vector2 point = ToReference(touch.position);
                if (touch.phase == TouchPhase.Began && beganCount < beganPositions.Length)
                    beganPositions[beganCount++] = point;

                if (!gameplayActive || touch.phase == TouchPhase.Ended || touch.phase == TouchPhase.Canceled)
                    continue;

                if (point.x < 700f && point.y > 560f)
                {
                    Vector2 candidate = (point - StickCenter) / StickRadius;
                    if (candidate.sqrMagnitude > move.sqrMagnitude)
                        move = Vector2.ClampMagnitude(new Vector2(candidate.x, -candidate.y), 1f);
                }

                if (touch.phase != TouchPhase.Began)
                    continue;
                if (Vector2.Distance(point, PunchCenter) <= ActionRadius)
                    punchFrame = Time.frameCount;
                else if (Vector2.Distance(point, JumpCenter) <= ActionRadius)
                    jumpFrame = Time.frameCount;
                else if (Vector2.Distance(point, KickCenter) <= ActionRadius)
                    kickFrame = Time.frameCount;
                else if (Vector2.Distance(point, HeavyCenter) <= ActionRadius)
                    heavyFrame = Time.frameCount;
                else if (Vector2.Distance(point, SpecialCenter) <= ActionRadius)
                    specialFrame = Time.frameCount;
                else if (Vector2.Distance(point, GrabCenter) <= ActionRadius)
                    grabFrame = Time.frameCount;
                else if (Vector2.Distance(point, TeamCenter) <= ActionRadius)
                    teamFrame = Time.frameCount;
                else if (Vector2.Distance(point, MenuCenter) <= 92f)
                    cancelFrame = Time.frameCount;
            }
        }

        private static Vector2 ToReference(Vector2 screenPoint) => new Vector2(
            screenPoint.x * ReferenceWidth / Mathf.Max(1f, Screen.width),
            (Screen.height - screenPoint.y) * ReferenceHeight / Mathf.Max(1f, Screen.height));

        private void OnGUI()
        {
            if (!touchAvailable || !gameplayActive)
                return;

            GUI.matrix = Matrix4x4.Scale(new Vector3(
                Screen.width / ReferenceWidth, Screen.height / ReferenceHeight, 1f));
            GUIStyle circle = new GUIStyle(GUI.skin.box)
            {
                alignment = TextAnchor.MiddleCenter,
                fontSize = 21,
                fontStyle = FontStyle.Bold,
                normal = { textColor = Color.white }
            };
            GUIStyle hint = new GUIStyle(GUI.skin.label)
            {
                alignment = TextAnchor.MiddleCenter,
                fontSize = 22,
                fontStyle = FontStyle.Bold,
                normal = { textColor = new Color(0.72f, 0.96f, 1f, 0.9f) }
            };

            Color previous = GUI.color;
            GUI.color = new Color(0.15f, 0.9f, 0.92f, 0.55f);
            GUI.Box(CenteredRect(StickCenter, 308f), string.Empty, circle);
            Vector2 knob = StickCenter + new Vector2(move.x, -move.y) * 92f;
            GUI.color = new Color(0.72f, 0.96f, 1f, 0.75f);
            GUI.Box(CenteredRect(knob, 112f), string.Empty, circle);

            DrawAction(GrabCenter, "GRAB", new Color(0.95f, 0.58f, 0.2f, 0.74f), circle);
            DrawAction(HeavyCenter, "HEAVY", new Color(0.78f, 0.38f, 0.92f, 0.74f), circle);
            DrawAction(SpecialCenter, "SPECIAL", new Color(0.12f, 0.78f, 0.9f, 0.74f), circle);
            DrawAction(TeamCenter, teamReady ? "TEAM!" : "TEAM",
                teamReady ? new Color(0.72f, 1f, 0.12f, 0.95f) : new Color(0.35f, 0.45f, 0.25f, 0.62f), circle);
            DrawAction(JumpCenter, "JUMP", new Color(0.4f, 0.72f, 1f, 0.7f), circle);
            DrawAction(KickCenter, "KICK", new Color(1f, 0.72f, 0.18f, 0.74f), circle);
            DrawAction(PunchCenter, "PUNCH", new Color(1f, 0.34f, 0.4f, 0.74f), circle);
            GUI.color = new Color(0.12f, 0.16f, 0.28f, 0.82f);
            GUI.Box(CenteredRect(MenuCenter, 150f), "II", circle);
            GUI.color = previous;
            GUI.Label(new Rect(82f, 1005f, 340f, 48f), "DRAG TO MOVE", hint);
        }

        private static Rect CenteredRect(Vector2 center, float size) =>
            new Rect(center.x - size * 0.5f, center.y - size * 0.5f, size, size);

        private static void DrawAction(Vector2 center, string label, Color color, GUIStyle style)
        {
            GUI.color = color;
            GUI.Box(CenteredRect(center, ActionRadius * 1.72f), label, style);
        }
    }
}
