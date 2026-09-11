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
        public static void BuildArcadeRelease()
        {
            Controller226Build.ConfigureAxes();Controller226Validation.Run();Controller229Validation.Run();
            Essa222Validation.Run(true);Motion225Validation.Run();Repairs232Validation.Run();Arcade234Validation.Run();
            BuildAndroid("Builds/Android/FamilyForceUnity-Arcade-0.5.11.apk",BuildOptions.None,"0.5.11-arcade",12);
        }
        public static void BuildRepairsRelease()
        {
            Controller226Build.ConfigureAxes();Controller226Validation.Run();Controller229Validation.Run();
            Essa222Validation.Run(true);Motion225Validation.Run();Repairs232Validation.Run();
            BuildAndroid("Builds/Android/FamilyForceUnity-Repairs-0.5.10.apk",BuildOptions.None,"0.5.10-repairs",11);
        }
        public static void BuildTvInputRelease()
        {
            Controller226Build.ConfigureAxes();Controller226Validation.Run();Controller229Validation.Run();
            Essa222Validation.Run(true);Motion225Validation.Run();
            BuildAndroid("Builds/Android/FamilyForceUnity-TVInput-0.5.9.apk",BuildOptions.None,"0.5.9-tv-input",10);
        }

        public static void BuildTvInstallRelease()
        {
            Controller226Build.ConfigureAxes();
            Controller226Validation.Run();
            Essa222Validation.Run(true);
            BuildAndroid("Builds/Android/FamilyForceUnity-TVInstall-0.5.8.apk",
                BuildOptions.None,"0.5.8-tv-install",9);
        }

        public static void BuildControllerRelease()
        {
            Controller226Build.ConfigureAxes();
            Controller226Validation.Run();
            Essa222Validation.Run(true);
            BuildAndroid("Builds/Android/FamilyForceUnity-Controllers-0.5.7.apk",
                BuildOptions.None,"0.5.7-controllers",8);
        }

        public static void BuildSmoothRelease()
        {
            Essa222Validation.Run(true);
            Motion225Validation.Run();
            BuildAndroid("Builds/Android/FamilyForceUnity-Smooth-0.5.6.apk",
                BuildOptions.None, "0.5.6-smooth", 7);
        }

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
            PlayerSettings.Android.preferredInstallLocation = AndroidPreferredInstallLocation.ForceInternal;
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
