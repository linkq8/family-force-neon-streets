using System.IO;
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.Build.Reporting;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;

namespace FamilyForce.Unity.Editor
{
    public static class BuildFamilyForce
    {
        private const string ScenePath = "Assets/FamilyForce/Scenes/Prototype.unity";

        public static void BuildUpdaterRelease()
        {
            Essa222Validation.Run();
            BuildAndroid("Builds/Android/FamilyForceUnity-Updates-0.5.5.apk",
                BuildOptions.None, "0.5.5-updates", 6);
        }

        public static void BuildEssaClearRelease()
        {
            Essa222Validation.Run();
            BuildAndroid("Builds/Android/FamilyForceUnity-EssaClear-0.5.4.apk",
                BuildOptions.None, "0.5.4-essa-clear-fast", 5);
        }

        public static void BuildEssaVideoRelease()
        {
            Essa221Validation.Run();
            BuildAndroid("Builds/Android/FamilyForceUnity-EssaVideo-0.5.3.apk",
                BuildOptions.None, "0.5.3-essa-video", 4);
        }

        [MenuItem("Family Force/Build Essa Motion Fix Android v0.5.2")]
        public static void BuildEssaMotionRelease()
        {
            BuildAndroid("Builds/Android/FamilyForceUnity-EssaMotion-0.5.2.apk",
                BuildOptions.None, "0.5.2-essa-motion-fix", 3);
        }

        [MenuItem("Family Force/Build Essa Retro Android v0.5.1")]
        public static void BuildEssaRetroRelease()
        {
            BuildAndroid("Builds/Android/FamilyForceUnity-EssaRetro-0.5.1.apk",
                BuildOptions.None, "0.5.1-essa-retro", 2);
        }

        [MenuItem("Family Force/Build Android TV Prototype")]
        public static void BuildAndroidPrototype()
        {
            BuildAndroid("Builds/Android/FamilyForceUnityPrototype.apk",
                BuildOptions.Development);
        }

        [MenuItem("Family Force/Build Android TV Atlas Prototype (Production)")]
        public static void BuildAndroidAtlasPrototype()
        {
            BuildAndroid("Builds/Android/FamilyForceUnityAtlasPrototype.apk",
                BuildOptions.None);
        }

        private static void BuildAndroid(string outputPath, BuildOptions buildOptions,
            string version = "0.5.0-stage-one-slice", int versionCode = 1)
        {
            ConfigureProject();
            PlayerSettings.bundleVersion = version;
            PlayerSettings.Android.bundleVersionCode = versionCode;
            AssetDatabase.SaveAssets();
            EnsureScene();
            Directory.CreateDirectory("Builds/Android");
            var options = new BuildPlayerOptions
            {
                scenes = new[] { ScenePath },
                locationPathName = outputPath,
                target = BuildTarget.Android,
                options = buildOptions
            };
            BuildReport report = BuildPipeline.BuildPlayer(options);
            if (report.summary.result != BuildResult.Succeeded)
                throw new BuildFailedException($"Android build failed: {report.summary.result}");
            Debug.Log($"UNITY_APK={Path.GetFullPath(options.locationPathName)}");
        }

        private static void ConfigureProject()
        {
            FamilyForceAtlasBuilder.RebuildAll();
            FamilyForceAtlasBuilder.ValidateAll();
            PlayerSettings.companyName = "Family Force";
            PlayerSettings.productName = "Family Force Unity Prototype";
            PlayerSettings.bundleVersion = "0.5.0-stage-one-slice";
            PlayerSettings.SetApplicationIdentifier(NamedBuildTarget.Android,
                "com.familyforce.neonstreets.unityprototype");
            PlayerSettings.defaultInterfaceOrientation = UIOrientation.LandscapeLeft;
            PlayerSettings.fullScreenMode = FullScreenMode.FullScreenWindow;
            PlayerSettings.Android.minSdkVersion = AndroidSdkVersions.AndroidApiLevel25;
            PlayerSettings.Android.targetSdkVersion = AndroidSdkVersions.AndroidApiLevelAuto;
            PlayerSettings.Android.targetArchitectures = AndroidArchitecture.ARMv7 | AndroidArchitecture.ARM64;
            PlayerSettings.Android.androidTVCompatibility = true;
            PlayerSettings.Android.androidIsGame = true;
            PlayerSettings.SetGraphicsAPIs(BuildTarget.Android,
                new[] { GraphicsDeviceType.OpenGLES3 });
            PlayerSettings.SetScriptingBackend(NamedBuildTarget.Android,
                ScriptingImplementation.IL2CPP);
            SetActiveInputHandlingToBoth();
            EditorUserBuildSettings.buildAppBundle = false;
            EditorUserBuildSettings.androidBuildSystem = AndroidBuildSystem.Gradle;
            AssetDatabase.SaveAssets();
        }

        private static void SetActiveInputHandlingToBoth()
        {
            Object[] settings = AssetDatabase.LoadAllAssetsAtPath("ProjectSettings/ProjectSettings.asset");
            if (settings.Length == 0)
                return;
            var serialized = new SerializedObject(settings[0]);
            SerializedProperty input = serialized.FindProperty("activeInputHandler");
            if (input == null)
                return;
            input.intValue = 2; // Both: Input System + legacy Android TV key fallback.
            serialized.ApplyModifiedPropertiesWithoutUndo();
        }

        private static void EnsureScene()
        {
            Directory.CreateDirectory(Path.GetDirectoryName(ScenePath));
            if (!File.Exists(ScenePath))
            {
                var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
                new GameObject("GameBootstrap").AddComponent<GameBootstrap>();
                EditorSceneManager.SaveScene(scene, ScenePath);
            }
            EditorBuildSettings.scenes = new[] { new EditorBuildSettingsScene(ScenePath, true) };
        }
    }
}
