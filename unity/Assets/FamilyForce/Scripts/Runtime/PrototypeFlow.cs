using UnityEngine;

namespace FamilyForce.Unity
{
    public sealed class PrototypeFlow : MonoBehaviour
    {
        private enum ScreenState { Menu, CharacterSelect, Playing, Results }

        private readonly UnifiedInput p1Input = new UnifiedInput(0, true);
        private readonly UnifiedInput p2Input = new UnifiedInput(1, false);
        private readonly string[] options = { "START — 1 PLAYER", "START — 2 PLAYERS", "INPUT TEST", "EXIT" };
        private readonly string[] actors = { CharacterAtlasCatalog.Essa, CharacterAtlasCatalog.Adam };
        private readonly int[] actorSelection = { 0, 1 };
        private readonly bool[] confirmed = new bool[2];
        private readonly Sprite[] portraits = new Sprite[2];
        private readonly float[] horizontalLatch = new float[2];
        private int selected;
        private float verticalLatch;
        private bool twoPlayersRequested;
        private ScreenState state;
        private PlayerMotor playerOne;
        private PlayerMotor playerTwo;
        private CombatDirector combat;
        private int finalScore;
        private int highScore;
        private float clearTime;

        public void BindPlayers(PlayerMotor p1, PlayerMotor p2, CombatDirector combatDirector)
        {
            playerOne = p1;
            playerTwo = p2;
            combat = combatDirector;
            combat.StageCompleted += OnStageCompleted;
            combat.SetCombatActive(false, false);
            TouchInputOverlay.SetGameplayActive(false);
            state = ScreenState.Menu;
            highScore = PlayerPrefs.GetInt("FF_STAGE1_HIGH_SCORE", 0);
            portraits[0] = CharacterAtlasCatalog.LoadClip(CharacterAtlasCatalog.Essa, "idle")[0];
            portraits[1] = CharacterAtlasCatalog.LoadClip(CharacterAtlasCatalog.Adam, "idle")[0];
        }

        private void Update()
        {
            switch (state)
            {
                case ScreenState.Playing:
                    if (p1Input.CancelPressed())
                        ReturnToMenu();
                    break;
                case ScreenState.Results:
                    if (p1Input.ConfirmPressed())
                        BeginCharacterSelect();
                    else if (p1Input.CancelPressed())
                        ReturnToMenu();
                    break;
                case ScreenState.CharacterSelect:
                    UpdateCharacterSelect();
                    break;
                default:
                    UpdateMenu();
                    break;
            }
        }

        private void UpdateMenu()
        {
            for (int index = 0; index < options.Length; index++)
            {
                if (!TouchInputOverlay.BeganInside(OptionRect(index)))
                    continue;
                selected = index;
                ActivateSelection();
                return;
            }
            float y = p1Input.ReadMove().y;
            if (Mathf.Abs(y) < 0.35f)
                verticalLatch = 0f;
            else if (verticalLatch == 0f)
            {
                selected = (selected + (y < 0f ? 1 : -1) + options.Length) % options.Length;
                verticalLatch = Mathf.Sign(y);
            }
            if (p1Input.ConfirmPressed())
                ActivateSelection();
        }

        private void ActivateSelection()
        {
            if (selected == 3)
                Application.Quit();
            else if (selected < 2)
            {
                twoPlayersRequested = selected == 1;
                BeginCharacterSelect();
            }
        }

        private void BeginCharacterSelect()
        {
            confirmed[0] = false;
            confirmed[1] = false;
            horizontalLatch[0] = horizontalLatch[1] = 0f;
            state = ScreenState.CharacterSelect;
        }

        private void UpdateCharacterSelect()
        {
            HandleCharacterTouch(0, new Rect(430, 315, 500, 330));
            if (twoPlayersRequested)
                HandleCharacterTouch(1, new Rect(990, 315, 500, 330));
            UpdateCharacterPlayer(0, p1Input);
            if (twoPlayersRequested)
                UpdateCharacterPlayer(1, p2Input);
            if (p1Input.CancelPressed())
            {
                if (confirmed[0])
                    confirmed[0] = false;
                else
                    state = ScreenState.Menu;
                return;
            }
            if (confirmed[0] && (!twoPlayersRequested || confirmed[1]))
                StartStage();
        }

        private void HandleCharacterTouch(int index, Rect rect)
        {
            if (confirmed[index])
                return;
            Rect confirmRect = new Rect(rect.x, rect.yMax - 95f, rect.width, 95f);
            Rect selectRect = new Rect(rect.x, rect.y, rect.width, rect.height - 95f);
            if (TouchInputOverlay.BeganInside(confirmRect))
                confirmed[index] = true;
            else if (TouchInputOverlay.BeganInside(selectRect))
                actorSelection[index] = (actorSelection[index] + 1) % actors.Length;
        }

        private void UpdateCharacterPlayer(int index, UnifiedInput input)
        {
            if (confirmed[index])
                return;
            float x = input.ReadMove().x;
            if (Mathf.Abs(x) < 0.35f)
                horizontalLatch[index] = 0f;
            else if (horizontalLatch[index] == 0f)
            {
                actorSelection[index] = (actorSelection[index] + (x > 0f ? 1 : -1) + actors.Length) % actors.Length;
                horizontalLatch[index] = Mathf.Sign(x);
            }
            if (input.ConfirmPressed())
                confirmed[index] = true;
        }

        private void StartStage()
        {
            combat.SelectCharacters(actors[actorSelection[0]], actors[actorSelection[1]]);
            state = ScreenState.Playing;
            combat.SetCombatActive(true, twoPlayersRequested);
            TouchInputOverlay.SetGameplayActive(true);
        }

        private void OnStageCompleted(int score, float seconds)
        {
            finalScore = score;
            clearTime = seconds;
            highScore = Mathf.Max(highScore, score);
            PlayerPrefs.SetInt("FF_STAGE1_HIGH_SCORE", highScore);
            PlayerPrefs.Save();
            combat.SetCombatActive(false, false);
            TouchInputOverlay.SetGameplayActive(false);
            state = ScreenState.Results;
        }

        private void ReturnToMenu()
        {
            combat.SetCombatActive(false, false);
            TouchInputOverlay.SetGameplayActive(false);
            state = ScreenState.Menu;
        }

        private static Rect OptionRect(int index) => new Rect(610, 350 + index * 96, 700, 72);

        private void OnGUI()
        {
            GUI.matrix = Matrix4x4.Scale(new Vector3(Screen.width / 1920f, Screen.height / 1080f, 1f));
            GUIStyle title = new GUIStyle(GUI.skin.label) { fontSize = 52, fontStyle = FontStyle.Bold,
                alignment = TextAnchor.MiddleCenter, normal = { textColor = new Color(0.98f, 0.77f, 0.18f) } };
            GUIStyle item = new GUIStyle(GUI.skin.box) { fontSize = 32, fontStyle = FontStyle.Bold,
                alignment = TextAnchor.MiddleCenter };

            if (state == ScreenState.Playing)
            {
                GUI.Box(new Rect(38, 32, 340, 68), $"P1  {playerOne.InputLabel}", item);
                if (combat.TwoPlayers)
                    GUI.Box(new Rect(1542, 32, 340, 68), $"P2  {playerTwo.InputLabel}", item);
                return;
            }
            GUI.Box(new Rect(350, 120, 1220, 760), GUIContent.none);
            if (state == ScreenState.CharacterSelect)
            {
                GUI.Label(new Rect(430, 175, 1060, 90), "CHOOSE YOUR HERO", title);
                DrawCharacterPanel(0, new Rect(430, 315, 500, 330), item);
                if (twoPlayersRequested)
                    DrawCharacterPanel(1, new Rect(990, 315, 500, 330), item);
                else
                    GUI.Box(new Rect(990, 315, 500, 330), "P2  OPTIONAL\n\nAI COMPANION ENABLED", item);
                GUI.Label(new Rect(480, 700, 960, 70), twoPlayersRequested
                    ? "BOTH PLAYERS MUST CONFIRM"
                    : "LEFT / RIGHT TO CHOOSE  •  CONFIRM TO START", item);
                return;
            }
            if (state == ScreenState.Results)
            {
                GUI.Label(new Rect(430, 175, 1060, 90), "STAGE CLEAR!", title);
                GUI.Box(new Rect(570, 320, 780, 100), $"SCORE     {finalScore:000000}", item);
                GUI.Box(new Rect(570, 440, 780, 100), $"HIGH SCORE     {highScore:000000}", item);
                GUI.Box(new Rect(570, 560, 780, 100), $"TIME     {clearTime:0.0} SEC", item);
                GUI.Label(new Rect(510, 720, 900, 60), "CONFIRM: PLAY AGAIN  •  BACK: MENU", item);
                return;
            }
            GUI.Label(new Rect(430, 175, 1060, 90), "FAMILY FORCE — UNITY", title);
            GUI.Label(new Rect(510, 270, 900, 55), $"ACTIVE INPUT: {p1Input.DeviceLabel}", item);
            for (int index = 0; index < options.Length; index++)
            {
                Color previous = GUI.color;
                GUI.color = index == selected ? new Color(1f, 0.78f, 0.18f) : Color.white;
                GUI.Box(OptionRect(index), index == selected ? $">  {options[index]}  <" : options[index], item);
                GUI.color = previous;
            }
            GUI.Label(new Rect(510, 760, 900, 55), TouchInputOverlay.IsAvailable
                ? "TAP OR USE CONTROLLER / REMOTE"
                : "D-PAD TO MOVE  •  SOUTH / ENTER TO SELECT", item);
        }

        private void DrawCharacterPanel(int playerIndex, Rect rect, GUIStyle style)
        {
            string actor = actors[actorSelection[playerIndex]].ToUpperInvariant();
            string status = confirmed[playerIndex] ? "READY!" : "<  SELECT  >";
            Color previous = GUI.color;
            GUI.color = confirmed[playerIndex] ? new Color(0.45f, 1f, 0.45f) : Color.white;
            GUI.Box(rect, GUIContent.none, style);
            GUI.Label(new Rect(rect.x, rect.y + 16f, rect.width, 48f),
                $"P{playerIndex + 1} — {actor}", style);
            DrawSprite(portraits[actorSelection[playerIndex]],
                new Rect(rect.center.x - 82f, rect.y + 72f, 164f, 164f));
            GUI.Label(new Rect(rect.x + 30f, rect.yMax - 78f, rect.width - 60f, 56f), status, style);
            GUI.color = previous;
        }

        private static void DrawSprite(Sprite sprite, Rect rect)
        {
            if (sprite == null || sprite.texture == null)
                return;
            Rect source = sprite.textureRect;
            Rect uv = new Rect(source.x / sprite.texture.width, source.y / sprite.texture.height,
                source.width / sprite.texture.width, source.height / sprite.texture.height);
            GUI.DrawTextureWithTexCoords(rect, sprite.texture, uv, true);
        }
    }
}
