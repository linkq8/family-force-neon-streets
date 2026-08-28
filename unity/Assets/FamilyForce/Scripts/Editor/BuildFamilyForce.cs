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

        [MenuItem("Family Force/Build Android TV Prototype")]
        public static void BuildAndroidPrototype()
        {
            ConfigureProject();
            EnsureScene();
            Directory.CreateDirectory("Builds/Android");
            var options = new BuildPlayerOptions
            {
                scenes = new[] { ScenePath },
                locationPathName = "Builds/Android/FamilyForceUnityPrototype.apk",
                target = BuildTarget.Android,
                options = BuildOptions.Development
            };
            BuildReport report = BuildPipeline.BuildPlayer(options);
            if (report.summary.result != BuildResult.Succeeded)
                throw new BuildFailedException($"Android build failed: {report.summary.result}");
            Debug.Log($"UNITY_APK={Path.GetFullPath(options.locationPathName)}");
        }

        private static void ConfigureProject()
        {
            PlayerSettings.companyName = "Family Force";
            PlayerSettings.productName = "Family Force Unity Prototype";
            PlayerSettings.bundleVersion = "0.1.0-migration";
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
            AssetDatabase.ImportAsset("Assets/FamilyForce/Resources/Heroes/parent_idle.png",
                ImportAssetOptions.ForceUpdate);
            AssetDatabase.ImportAsset("Assets/FamilyForce/Resources/Heroes/parent_walk.png",
                ImportAssetOptions.ForceUpdate);
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
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            new GameObject("GameBootstrap").AddComponent<GameBootstrap>();
            EditorSceneManager.SaveScene(scene, ScenePath);
            EditorBuildSettings.scenes = new[] { new EditorBuildSettingsScene(ScenePath, true) };
        }
    }
}
