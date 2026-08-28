using UnityEngine;

namespace FamilyForce.Unity
{
    public sealed class PrototypeFlow : MonoBehaviour
    {
        private readonly UnifiedInput input = new UnifiedInput();
        private readonly string[] options =
        {
            "START — 1 PLAYER",
            "START — 2 PLAYERS",
            "INPUT TEST",
            "EXIT"
        };
        private int selected;
        private float verticalLatch;
        private bool playing;
        private PlayerMotor playerOne;
        private PlayerMotor playerTwo;
        private CombatDirector combat;

        public void BindPlayers(PlayerMotor p1, PlayerMotor p2, CombatDirector combatDirector)
        {
            playerOne = p1;
            playerTwo = p2;
            combat = combatDirector;
            combat.SetCombatActive(false, false);
            TouchInputOverlay.SetGameplayActive(false);
        }

        private void Update()
        {
            if (playing)
            {
                if (input.CancelPressed())
                {
                    playing = false;
                    combat.SetCombatActive(false, false);
                    TouchInputOverlay.SetGameplayActive(false);
                }
                return;
            }

            for (int index = 0; index < options.Length; index++)
            {
                if (!TouchInputOverlay.BeganInside(OptionRect(index)))
                    continue;
                selected = index;
                ActivateSelection();
                return;
            }

            float y = input.ReadMove().y;
            if (Mathf.Abs(y) < 0.35f)
                verticalLatch = 0f;
            else if (verticalLatch == 0f)
            {
                selected = (selected + (y < 0f ? 1 : -1) + options.Length) % options.Length;
                verticalLatch = Mathf.Sign(y);
            }

            if (!input.ConfirmPressed())
                return;
            ActivateSelection();
        }

        private void ActivateSelection()
        {
            if (selected == 3)
                Application.Quit();
            else if (selected == 0 || selected == 1)
            {
                playing = true;
                combat.SetCombatActive(true, selected == 1);
                TouchInputOverlay.SetGameplayActive(true);
            }
        }

        private static Rect OptionRect(int index) =>
            new Rect(610, 350 + index * 96, 700, 72);

        private void OnGUI()
        {
            GUI.matrix = Matrix4x4.Scale(new Vector3(Screen.width / 1920f, Screen.height / 1080f, 1f));
            GUIStyle title = new GUIStyle(GUI.skin.label)
            {
                fontSize = 52,
                fontStyle = FontStyle.Bold,
                alignment = TextAnchor.MiddleCenter,
                normal = { textColor = new Color(0.98f, 0.77f, 0.18f) }
            };
            GUIStyle item = new GUIStyle(GUI.skin.box)
            {
                fontSize = 32,
                fontStyle = FontStyle.Bold,
                alignment = TextAnchor.MiddleCenter
            };

            if (playing)
            {
                GUI.Box(new Rect(38, 32, 340, 68), $"P1  {playerOne.InputLabel}", item);
                if (combat.TwoPlayers)
                    GUI.Box(new Rect(1542, 32, 340, 68), $"P2  {playerTwo.InputLabel}", item);
                return;
            }

            GUI.Box(new Rect(350, 120, 1220, 760), GUIContent.none);
            GUI.Label(new Rect(430, 175, 1060, 90), "FAMILY FORCE — UNITY MIGRATION", title);
            GUI.Label(new Rect(510, 270, 900, 55), $"ACTIVE INPUT: {input.DeviceLabel}", item);
            for (int index = 0; index < options.Length; index++)
            {
                Color previous = GUI.color;
                GUI.color = index == selected ? new Color(1f, 0.78f, 0.18f) : Color.white;
                GUI.Box(OptionRect(index),
                    index == selected ? $">  {options[index]}  <" : options[index], item);
                GUI.color = previous;
            }
            GUI.Label(new Rect(510, 760, 900, 55), TouchInputOverlay.IsAvailable
                ? "TAP AN OPTION  •  CONTROLLER AND REMOTE ALSO SUPPORTED"
                : "D-PAD TO MOVE  •  SOUTH / ENTER TO SELECT", item);
        }
    }
}
