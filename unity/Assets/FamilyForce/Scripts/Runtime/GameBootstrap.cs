using UnityEngine;

namespace FamilyForce.Unity
{
    public sealed class GameBootstrap : MonoBehaviour
    {
        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        private static void StartGame()
        {
            if (FindFirstObjectByType<GameBootstrap>() == null)
                new GameObject("GameBootstrap").AddComponent<GameBootstrap>();
        }

        private void Awake()
        {
            Application.targetFrameRate = 60;
            QualitySettings.vSyncCount = 0;
            Screen.sleepTimeout = SleepTimeout.NeverSleep;
            BuildCamera();
            BuildStage();
            gameObject.AddComponent<TouchInputOverlay>();
            GameObject playerOne = BuildHero("P1_Essa", CharacterAtlasCatalog.Essa,
                new Vector3(-4f, -2.15f, 0f), 3.45f, 20);
            GameObject playerTwo = BuildHero("P2_Adam", CharacterAtlasCatalog.Adam,
                new Vector3(-5.1f, -2.65f, 0f), 2.65f, 21);
            CombatDirector combat = gameObject.AddComponent<CombatDirector>();
            EnemyCombatant enemy = BuildEnemy(combat);
            combat.Initialize(playerOne.GetComponent<PlayerMotor>(),
                playerTwo.GetComponent<PlayerMotor>(), enemy);
            PrototypeFlow flow = gameObject.AddComponent<PrototypeFlow>();
            flow.BindPlayers(playerOne.GetComponent<PlayerMotor>(),
                playerTwo.GetComponent<PlayerMotor>(), combat);
        }

        private static void BuildCamera()
        {
            Camera camera = Camera.main;
            if (camera == null)
            {
                var cameraObject = new GameObject("Main Camera");
                cameraObject.tag = "MainCamera";
                camera = cameraObject.AddComponent<Camera>();
            }
            camera.orthographic = true;
            camera.orthographicSize = 5f;
            camera.transform.position = new Vector3(0f, 0f, -10f);
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = new Color(0.025f, 0.035f, 0.09f);
        }

        private static void BuildStage()
        {
            CreatePanel("Sky", new Vector3(0f, 1.3f, 2f), new Vector2(19f, 6.8f),
                new Color(0.08f, 0.07f, 0.18f));
            CreatePanel("Street", new Vector3(0f, -2.4f, 1f), new Vector2(19f, 3.5f),
                new Color(0.11f, 0.16f, 0.22f));
            for (int index = 0; index < 9; index++)
            {
                float x = -8f + index * 2f;
                CreatePanel($"Neon_{index}", new Vector3(x, 1.4f, 0.5f), new Vector2(1.1f, 0.18f),
                    index % 2 == 0 ? new Color(0.05f, 0.85f, 0.9f) : new Color(0.95f, 0.2f, 0.55f));
            }
        }

        private static GameObject BuildHero(string objectName, string actor, Vector3 position,
            float scale, int sortingOrder)
        {
            var player = new GameObject(objectName);
            player.transform.position = position;
            SpriteRenderer renderer = player.AddComponent<SpriteRenderer>();
            renderer.sortingOrder = sortingOrder;
            var animator = player.AddComponent<SpriteStripAnimator>();
            Sprite[] idle = CharacterAtlasCatalog.LoadClip(actor, "idle");
            Sprite[] walk = CharacterAtlasCatalog.LoadClip(actor, "walk");
            animator.Initialize(idle, walk);
            player.AddComponent<PlayerMotor>();
            player.transform.localScale = Vector3.one * scale;
            Debug.Log($"FF_UNITY: hero={actor} created idle={idle.Length} walk={walk.Length} " +
                $"sprite={(renderer.sprite != null)}");
            return player;
        }

        private static EnemyCombatant BuildEnemy(CombatDirector combat)
        {
            var enemyObject = new GameObject("Stage1_Grunt");
            SpriteRenderer renderer = enemyObject.AddComponent<SpriteRenderer>();
            renderer.sortingOrder = 19;
            enemyObject.AddComponent<SpriteStripAnimator>();
            EnemyCombatant enemy = enemyObject.AddComponent<EnemyCombatant>();
            enemyObject.transform.localScale = Vector3.one * 3.05f;
            enemy.Initialize(CharacterAtlasCatalog.Grunt, combat);
            return enemy;
        }

        private static void CreatePanel(string name, Vector3 position, Vector2 size, Color color)
        {
            var texture = new Texture2D(1, 1, TextureFormat.RGBA32, false)
            {
                filterMode = FilterMode.Point,
                wrapMode = TextureWrapMode.Clamp
            };
            texture.SetPixel(0, 0, color);
            texture.Apply(false, true);
            Sprite sprite = Sprite.Create(texture, new Rect(0, 0, 1, 1), new Vector2(0.5f, 0.5f), 1f);
            var panel = new GameObject(name);
            panel.transform.position = position;
            panel.transform.localScale = new Vector3(size.x, size.y, 1f);
            panel.AddComponent<SpriteRenderer>().sprite = sprite;
        }
    }
}
