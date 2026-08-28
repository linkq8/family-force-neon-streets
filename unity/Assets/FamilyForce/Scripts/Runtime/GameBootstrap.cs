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
            GameObject player = BuildPlayer();
            PrototypeFlow flow = gameObject.AddComponent<PrototypeFlow>();
            flow.BindPlayer(player);
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

        private static GameObject BuildPlayer()
        {
            var player = new GameObject("P1_Essa_Prototype");
            player.transform.position = new Vector3(-4f, -2.2f, 0f);
            SpriteRenderer renderer = player.AddComponent<SpriteRenderer>();
            renderer.sortingOrder = 20;
            var animator = player.AddComponent<SpriteStripAnimator>();
            Sprite[] idle = CharacterAtlasCatalog.LoadClip(CharacterAtlasCatalog.Essa, "idle");
            Sprite[] walk = CharacterAtlasCatalog.LoadClip(CharacterAtlasCatalog.Essa, "walk");
            animator.Initialize(idle, walk);
            player.AddComponent<PlayerMotor>();
            // The atlas contract uses 192 PPU; 3.45 preserves the prototype's
            // previous on-screen height without resizing any animation frame.
            player.transform.localScale = Vector3.one * 3.45f;
            Debug.Log($"FF_UNITY: player created idle={idle.Length} walk={walk.Length} " +
                $"sprite={(renderer.sprite != null)}");
            return player;
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
