using UnityEditor;
using UnityEngine;

namespace FamilyForce.Unity.Editor
{
    public sealed class FamilyForceTextureImporter : AssetPostprocessor
    {
        private void OnPreprocessTexture()
        {
            bool characterSource = assetPath.Contains("/FamilyForce/Art/Characters/");
            if (!assetPath.Contains("/FamilyForce/Resources/") && !characterSource)
                return;
            var importer = (TextureImporter)assetImporter;
            importer.textureType = characterSource
                ? TextureImporterType.Sprite
                : TextureImporterType.Default;
            if (characterSource)
            {
                importer.spriteImportMode = SpriteImportMode.Multiple;
                importer.spritePixelsPerUnit = 192f;
            }
            importer.alphaIsTransparency = true;
            importer.mipmapEnabled = false;
            importer.filterMode = FilterMode.Point;
            importer.wrapMode = TextureWrapMode.Clamp;
            importer.npotScale = TextureImporterNPOTScale.None;
            importer.textureCompression = TextureImporterCompression.Uncompressed;
            importer.maxTextureSize = 4096;
            var android = importer.GetPlatformTextureSettings("Android");
            android.overridden = true;
            android.maxTextureSize = 4096;
            android.format = TextureImporterFormat.RGBA32;
            android.textureCompression = TextureImporterCompression.Uncompressed;
            importer.SetPlatformTextureSettings(android);
        }
    }
}
