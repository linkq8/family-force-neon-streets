using System;
using System.Collections.Generic;
using System.IO;
using System.Reflection;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.InputSystem.LowLevel;

namespace FamilyForce.Unity.Editor
{
    /// <summary>Batch play-mode input/render smoke test, never runs in a player build.</summary>
    [InitializeOnLoad]
    public static class Essa201Playtest
    {
        const string Running = "FF_Essa201_QA";
        static readonly string Output = Path.GetFullPath("../art-pipeline/builds/Essa/motion-201/unity-test");
        static PlayerMotor hero;
        static SpriteRenderer renderer;
        static Keyboard keyboard;
        static float started;
        static int phase;
        static int captures;
        static float nextCapture;
        static float startX, rightX, leftX;
        static InputSettings.BackgroundBehavior previousBackground;
        static InputSettings.EditorInputBehaviorInPlayMode previousEditorInput;
        static KeyboardState desiredKeys;
        static readonly List<string> EditorWarnings = new List<string>();
        static readonly HashSet<string> Seen = new HashSet<string>();
        static readonly HashSet<string> SeenActions = new HashSet<string>();
        static bool jumpLift;
        static readonly List<string> Errors = new List<string>();

        static Essa201Playtest()
        {
            EditorApplication.update += Tick;
            Application.logMessageReceived += (message, trace, type) =>
            {
                if (SessionState.GetBool(Running, false) && hero != null && (type == LogType.Error || type == LogType.Exception || type == LogType.Assert))
                {
                    if (trace.Contains("UnityEditor.Search.")) EditorWarnings.Add(message);
                    else Errors.Add(message);
                }
            };
        }

        public static void Run()
        {
            Essa201AnimatorRegression.Run();
            Directory.CreateDirectory(Output);
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
            EditorSceneManager.OpenScene("Assets/FamilyForce/Scenes/Prototype.unity");
            SessionState.SetBool(Running, true);
            SessionState.SetFloat(Running + "Deadline", (float)EditorApplication.timeSinceStartup + 150f);
            EditorApplication.isPlaying = true;
        }

        static void Require(bool condition, string message)
        {
            if (!condition) throw new InvalidOperationException(message);
        }

        static void Tick()
        {
            if (!SessionState.GetBool(Running, false)) return;
            try
            {
                Require(EditorApplication.timeSinceStartup < SessionState.GetFloat(Running + "Deadline", 0), "Playtest timeout");
                if (!EditorApplication.isPlaying || EditorApplication.isCompiling) return;
                if (EditorApplication.isPaused) EditorApplication.isPaused = false;
                if (hero == null)
                {
                    GameObject obj = null;
                    foreach (var motor in UnityEngine.Object.FindObjectsByType<PlayerMotor>(FindObjectsInactive.Include, FindObjectsSortMode.None))
                        if (motor.gameObject.name == "P1_Essa") obj = motor.gameObject;
                    if (obj == null) return;
                    hero = obj.GetComponent<PlayerMotor>();
                    renderer = obj.GetComponent<SpriteRenderer>();
                    var flow = UnityEngine.Object.FindFirstObjectByType<PrototypeFlow>();
                    typeof(PrototypeFlow).GetMethod("StartStage", BindingFlags.Instance | BindingFlags.NonPublic).Invoke(flow, null);
                    keyboard = InputSystem.AddDevice<Keyboard>();
                    keyboard.MakeCurrent();
                    previousBackground = InputSystem.settings.backgroundBehavior;
                    InputSystem.settings.backgroundBehavior = InputSettings.BackgroundBehavior.IgnoreFocus;
                    previousEditorInput = InputSystem.settings.editorInputBehaviorInPlayMode;
                    InputSystem.settings.editorInputBehaviorInPlayMode = InputSettings.EditorInputBehaviorInPlayMode.AllDeviceInputAlwaysGoesToGameView;
                    InputSystem.onBeforeUpdate += Inject;
                    Application.runInBackground = true;
                    hero.ResetPosition(new Vector3(-5f, -2.8f, 0));
                    startX = hero.transform.position.x;
                    started = Time.realtimeSinceStartup + 3.2f; // Let the real stage intro enable controls.
                    var walk = CharacterAtlasCatalog.LoadClip("Essa", "walk");
                    Require(walk.Length == 12, "Walk must load twelve available source frames");
                    Require(CharacterAtlasCatalog.LoadClip("Essa", "idle").Length == 1, "Honest single-pose idle");
                    Require(!PracticalEssaClips.TryLoad("Adam", "walk", out _), "Adam untouched");
                    Require(PracticalEssaClips.TryLoad("Essa", "punch", out var punch) && punch[1].name == "Essa198_punch", "New punch pose missing");
                    foreach (string action in new[]{"idle","walk","punch","kick","heavy_punch","heavy_kick","jump","special","link","hurt","knockdown"})
                        foreach (var sprite in CharacterAtlasCatalog.LoadClip("Essa",action))
                            Require(sprite.name.StartsWith("Essa198_") || sprite.name.StartsWith("Essa201_"), "Unexpected legacy identity swap: " + action);
                    foreach (var sprite in walk)
                    {
                        Require(sprite.rect.width == 384 && sprite.rect.height == 384, "Wrong slicing");
                        Require(sprite.pivot == new Vector2(192,24), "Wrong fixed pivot");
                        Require(sprite.pixelsPerUnit == 384, "Wrong gameplay scale");
                        Require(sprite.texture == walk[0].texture, "Sprites must share one atlas texture");
                    }
                }
                float elapsed = Time.realtimeSinceStartup - started;
                if (elapsed < 0.5f) Key();
                else if (elapsed < 1.8f) Key(KeyCodeToInput.Right);
                else if (elapsed < 3.1f)
                {
                    if (phase < 1)
                    {
                        rightX = hero.transform.position.x;
                        Require(rightX > startX + 1, $"Right input did not move character: start={startX} end={rightX} key={keyboard.rightArrowKey.isPressed} frame={Time.frameCount} control={typeof(PlayerMotor).GetField("controlEnabled",BindingFlags.NonPublic|BindingFlags.Instance).GetValue(hero)}");
                        Require(!renderer.flipX, "Right facing incorrect");
                        Capture("right.png");
                        phase = 1;
                    }
                    Key(KeyCodeToInput.Left);
                }
                else if (elapsed < 3.6f)
                {
                    if (phase < 2)
                    {
                        leftX = hero.transform.position.x;
                        Require(leftX < rightX - 1, "Left input did not move character");
                        Require(renderer.flipX, "Left facing incorrect");
                        Capture("left.png");
                        phase = 2;
                    }
                    Key();
                }
                else if (elapsed < 8.5f)
                {
                    if (phase < 3)
                    {
                        Require(renderer.sprite.name == "Essa198_guard", "Idle did not restore practical pose");
                        Capture("idle.png");
                        hero.ResetPosition(new Vector3(-5f,-2.8f,0));
                        foreach (var enemy in UnityEngine.Object.FindObjectsByType<EnemyCombatant>(FindObjectsSortMode.None))
                        {
                            enemy.transform.position = new Vector3(6f,-2.8f,0);
                            enemy.enabled = false; // Isolate visual/input smoke test from enemy damage.
                        }
                        phase = 3;
                    }
                    if (elapsed < 3.72f) desiredKeys = new KeyboardState(UnityEngine.InputSystem.Key.J);
                    else if (elapsed >= 4.25f && elapsed < 4.37f) desiredKeys = new KeyboardState(UnityEngine.InputSystem.Key.L);
                    else if (elapsed >= 4.9f && elapsed < 5.02f) desiredKeys = new KeyboardState(UnityEngine.InputSystem.Key.U);
                    else if (elapsed >= 5.6f && elapsed < 5.72f) desiredKeys = new KeyboardState(UnityEngine.InputSystem.Key.I);
                    else if (elapsed >= 7.55f && elapsed < 7.67f) desiredKeys = new KeyboardState(UnityEngine.InputSystem.Key.K);
                    else Key();
                    if (elapsed >= 6.3f && phase < 4)
                    {
                        hero.PlayHurt();
                        phase = 4;
                    }
                    if (elapsed >= 6.85f && phase < 5)
                    {
                        hero.GetComponent<SpriteStripAnimator>().PlayOnce(CharacterAtlasCatalog.LoadClip("Essa","knockdown"));
                        phase = 5;
                    }
                    if (elapsed >= 7.6f && hero.transform.position.y > -2.55f) jumpLift = true;
                    string pose = renderer.sprite.name;
                    if (!pose.StartsWith("Essa198_walk_") && SeenActions.Add(pose))
                        Capture(pose + ".png");
                }
                else
                {
                    Require(renderer.sprite.name == "Essa198_guard", "Idle did not restore practical pose");
                    Require(Seen.Count == 12, "All twelve motion201 frames must actually be observed");
                    foreach (string pose in new[]{"punch","kick","uppercut","palm","hurt","down"})
                        Require(SeenActions.Contains("Essa198_"+pose), "Action not displayed: " + pose);
                    Require(jumpLift,"Jump input did not lift character");
                    Require(Errors.Count == 0, string.Join("\n", Errors));
                    Capture("idle.png");
                    File.WriteAllText(Path.Combine(Output,"result.json"),
                        $"{{\"status\":\"PASS\",\"right_input_moves\":true,\"left_input_moves\":true,\"flip_x\":true,\"idle_restore\":true,\"seen_walk_frames\":{Seen.Count},\"fixed_pivot\":[192,24],\"ppu\":384,\"shared_walk_texture\":true,\"all_11_clips_use_new_art\":true,\"punch_kick_heavy_special_keyboard_test\":true,\"hurt_knockdown_playback_test\":true,\"jump_keyboard_test\":true,\"enemy_ai_disabled_during_action_visual_test\":true,\"android_device_tested\":false}}");
                    Finish(0);
                    return;
                }
                if (renderer.sprite != null && renderer.sprite.name.StartsWith("Essa198_walk_")) Seen.Add(renderer.sprite.name);
                if (elapsed >= nextCapture && captures < 90)
                {
                    Capture($"frame-{captures++:00}.png");
                    nextCapture = elapsed + 0.1f;
                }
                EditorApplication.QueuePlayerLoopUpdate();
            }
            catch (Exception ex)
            {
                Directory.CreateDirectory(Output);
                File.WriteAllText(Path.Combine(Output,"failure.txt"), ex.ToString());
                Debug.LogException(ex);
                Finish(1);
            }
        }

        enum KeyCodeToInput { None, Right, Left }
        static void Key(KeyCodeToInput direction = KeyCodeToInput.None)
        {
            var state = direction == KeyCodeToInput.Right ? new KeyboardState(UnityEngine.InputSystem.Key.RightArrow)
                : direction == KeyCodeToInput.Left ? new KeyboardState(UnityEngine.InputSystem.Key.LeftArrow) : new KeyboardState();
            desiredKeys = state;
        }

        static void Inject()
        {
            if (keyboard != null && InputState.currentUpdateType == InputUpdateType.Dynamic)
                InputSystem.QueueStateEvent(keyboard, desiredKeys);
        }

        static void Capture(string name)
        {
            Camera camera = Camera.main;
            var rt = RenderTexture.GetTemporary(960,540,24,RenderTextureFormat.ARGB32);
            var previous = camera.targetTexture;
            var active = RenderTexture.active;
            camera.targetTexture = rt;
            camera.Render();
            RenderTexture.active = rt;
            var image = new Texture2D(960,540,TextureFormat.RGB24,false);
            image.ReadPixels(new Rect(0,0,960,540),0,0);
            image.Apply();
            File.WriteAllBytes(Path.Combine(Output,name),image.EncodeToPNG());
            camera.targetTexture = previous;
            RenderTexture.active = active;
            UnityEngine.Object.DestroyImmediate(image);
            RenderTexture.ReleaseTemporary(rt);
        }

        static void Finish(int code)
        {
            SessionState.SetBool(Running,false);
            InputSystem.settings.backgroundBehavior = previousBackground;
            InputSystem.settings.editorInputBehaviorInPlayMode = previousEditorInput;
            InputSystem.onBeforeUpdate -= Inject;
            if (EditorWarnings.Count > 0) File.WriteAllLines(Path.Combine(Output,"editor-warnings.txt"), EditorWarnings);
            if (keyboard != null) InputSystem.RemoveDevice(keyboard);
            Debug.Log($"ESSA201_PLAYTEST_EXIT={code}");
            EditorApplication.Exit(code);
        }
    }
}
