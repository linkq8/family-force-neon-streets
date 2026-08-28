using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.U2D;
using UnityEngine;
using UnityEngine.U2D;

namespace FamilyForce.Unity.Editor
{
    public static class FamilyForceAtlasBuilder
    {
        private const string ArtRoot = "Assets/FamilyForce/Art/Characters";
        private const string AtlasRoot = "Assets/FamilyForce/Resources/Atlases";
        private const string PropRoot = "Assets/FamilyForce/Art/Stage1Props";
        private const int CellHeight = 192;
        private const float PixelsPerUnit = 192f;

        private sealed class ActorSpec
        {
            public readonly string Name;
            public readonly string Folder;
            public readonly int DefaultColumns;
            public readonly bool LegacyGrid;

            public ActorSpec(string name, string folder, int columns, bool legacyGrid = false)
            {
                Name = name;
                Folder = folder;
                DefaultColumns = columns;
                LegacyGrid = legacyGrid;
            }
        }

        private static readonly ActorSpec[] Actors =
        {
            new("Essa", $"{ArtRoot}/Heroes/Essa", 12),
            new("Adam", $"{ArtRoot}/Heroes/Adam", 8),
            new("Grunt", $"{ArtRoot}/Stage1Enemies/Grunt", 6),
            new("Skater", $"{ArtRoot}/Stage1Enemies/Skater", 6, true),
            new("LanternCourier", $"{ArtRoot}/Stage1Enemies/LanternCourier", 6),
            new("MarketEnforcer", $"{ArtRoot}/Stage1Enemies/MarketEnforcer", 6),
            new("Keeper7", $"{ArtRoot}/Stage1Enemies/Keeper7", 6, true),
        };

        private static readonly string[] EnemyRows =
        {
            "idle", "walk", "attack_1", "attack_2", "hurt", "knockdown"
        };

        [MenuItem("Family Force/Rebuild Character Sprite Atlases")]
        public static void RebuildAll()
        {
            Directory.CreateDirectory(AtlasRoot);
            foreach (ActorSpec actor in Actors)
            {
                List<Texture2D> textures = ImportAndSlice(actor);
                CreateAtlas(actor, textures);
            }
            CreateStageOnePropsAtlas();
            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
            Debug.Log("FF_ATLAS: rebuilt 7 character atlases and Stage 1 props atlas");
        }

        public static void ValidateAll()
        {
            var atlases = new List<SpriteAtlas>();
            foreach (ActorSpec actor in Actors)
            {
                string path = AtlasPath(actor.Name);
                SpriteAtlas atlas = AssetDatabase.LoadAssetAtPath<SpriteAtlas>(path);
                if (atlas == null)
                    throw new InvalidOperationException($"Missing Sprite Atlas: {path}");
                atlases.Add(atlas);
            }

            SpriteAtlas props = AssetDatabase.LoadAssetAtPath<SpriteAtlas>(AtlasPath("Stage1Props"));
            if (props == null)
                throw new InvalidOperationException("Missing Stage 1 props Sprite Atlas");
            atlases.Add(props);

            // Packing every UHD character atlas in one editor call can exceed the
            // native packer's transient memory on Apple Silicon. Pack one at a
            // time; the emitted atlases are identical and the build is stable.
            foreach (SpriteAtlas atlas in atlases)
                SpriteAtlasUtility.PackAtlases(new[] { atlas }, BuildTarget.Android);
            foreach (ActorSpec actor in Actors)
            {
                SpriteAtlas atlas = AssetDatabase.LoadAssetAtPath<SpriteAtlas>(AtlasPath(actor.Name));
                int expected = ExpectedSpriteCount(actor);
                if (atlas.spriteCount != expected)
                    throw new InvalidOperationException(
                        $"{actor.Name} atlas expected {expected} sprites, got {atlas.spriteCount}");
                if (atlas.GetSprite($"{actor.Name}_idle_00") == null)
                    throw new InvalidOperationException($"{actor.Name} atlas has no idle frame");
                Debug.Log($"FF_ATLAS: {actor.Name} sprites={atlas.spriteCount}");
            }
            if (props.spriteCount != 1 || props.GetSprite("bat") == null)
                throw new InvalidOperationException("Stage 1 props atlas must contain bat");
            Debug.Log("FF_ATLAS: Stage1Props sprites=1");
        }

        private static void CreateStageOnePropsAtlas()
        {
            string batPath = $"{PropRoot}/bat.png";
            AssetDatabase.ImportAsset(batPath, ImportAssetOptions.ForceSynchronousImport);
            var importer = AssetImporter.GetAtPath(batPath) as TextureImporter;
            if (importer == null)
                throw new InvalidOperationException("Missing bat TextureImporter");
            importer.textureType = TextureImporterType.Sprite;
            importer.spriteImportMode = SpriteImportMode.Single;
            importer.spritePixelsPerUnit = 128f;
            importer.spritePivot = new Vector2(0.5f, 0.5f);
            importer.alphaIsTransparency = true;
            importer.mipmapEnabled = false;
            importer.filterMode = FilterMode.Point;
            importer.wrapMode = TextureWrapMode.Clamp;
            importer.npotScale = TextureImporterNPOTScale.None;
            importer.isReadable = false;
            importer.textureCompression = TextureImporterCompression.Uncompressed;
            importer.SaveAndReimport();
            Texture2D bat = AssetDatabase.LoadAssetAtPath<Texture2D>(batPath);
            CreateAtlas("Stage1Props", new UnityEngine.Object[] { bat });
        }

        private static List<Texture2D> ImportAndSlice(ActorSpec actor)
        {
            string[] paths = AssetDatabase.FindAssets("t:Texture2D", new[] { actor.Folder })
                .Select(AssetDatabase.GUIDToAssetPath)
                .Where(path => path.EndsWith(".png", StringComparison.OrdinalIgnoreCase))
                .OrderBy(path => path, StringComparer.Ordinal)
                .ToArray();
            if (paths.Length == 0)
                throw new InvalidOperationException($"No PNG sources found for {actor.Name}");

            var textures = new List<Texture2D>(paths.Length);
            foreach (string path in paths)
            {
                AssetDatabase.ImportAsset(path, ImportAssetOptions.ForceSynchronousImport);
                var importer = AssetImporter.GetAtPath(path) as TextureImporter;
                if (importer == null)
                    throw new InvalidOperationException($"No TextureImporter for {path}");

                Texture2D source = AssetDatabase.LoadAssetAtPath<Texture2D>(path);
                if (source == null || source.height % CellHeight != 0)
                    throw new InvalidOperationException($"Invalid character texture dimensions: {path}");

                importer.textureType = TextureImporterType.Sprite;
                importer.spriteImportMode = SpriteImportMode.Multiple;
                importer.spritePixelsPerUnit = PixelsPerUnit;
                importer.alphaIsTransparency = true;
                importer.mipmapEnabled = false;
                importer.filterMode = FilterMode.Point;
                importer.wrapMode = TextureWrapMode.Clamp;
                importer.npotScale = TextureImporterNPOTScale.None;
                importer.isReadable = false;
                importer.textureCompression = TextureImporterCompression.Uncompressed;

                SpriteMetaData[] slices = actor.LegacyGrid
                    ? SliceGrid(actor, source)
                    : SliceStrip(actor, path, source);
#pragma warning disable 618
                importer.spritesheet = slices;
#pragma warning restore 618
                importer.SaveAndReimport();
                textures.Add(AssetDatabase.LoadAssetAtPath<Texture2D>(path));
            }
            return textures;
        }

        private static SpriteMetaData[] SliceStrip(ActorSpec actor, string path, Texture2D source)
        {
            string action = Path.GetFileNameWithoutExtension(path);
            int columns = actor.Name == "MarketEnforcer" && action == "walk"
                ? 12 : actor.DefaultColumns;
            if (source.width % columns != 0 || source.height != CellHeight)
                throw new InvalidOperationException($"Invalid strip grid {actor.Name}/{action}");
            int cellWidth = source.width / columns;
            var slices = new SpriteMetaData[columns];
            for (int column = 0; column < columns; column++)
                slices[column] = Slice(actor.Name, action, column,
                    new Rect(column * cellWidth, 0, cellWidth, CellHeight));
            return slices;
        }

        private static SpriteMetaData[] SliceGrid(ActorSpec actor, Texture2D source)
        {
            const int columns = 6;
            const int rows = 6;
            if (source.width % columns != 0 || source.height != rows * CellHeight)
                throw new InvalidOperationException($"Invalid legacy grid for {actor.Name}");
            int cellWidth = source.width / columns;
            var slices = new SpriteMetaData[columns * rows];
            int index = 0;
            for (int row = 0; row < rows; row++)
            {
                int y = source.height - ((row + 1) * CellHeight);
                for (int column = 0; column < columns; column++)
                {
                    slices[index++] = Slice(actor.Name, EnemyRows[row], column,
                        new Rect(column * cellWidth, y, cellWidth, CellHeight));
                }
            }
            return slices;
        }

        private static SpriteMetaData Slice(string actor, string action, int frame, Rect rect)
        {
            return new SpriteMetaData
            {
                name = $"{actor}_{action}_{frame:00}",
                rect = rect,
                alignment = (int)SpriteAlignment.BottomCenter,
                pivot = new Vector2(0.5f, 0f),
                border = Vector4.zero
            };
        }

        private static void CreateAtlas(ActorSpec actor, List<Texture2D> textures)
        {
            CreateAtlas(actor.Name, textures.Cast<UnityEngine.Object>().ToArray());
        }

        private static void CreateAtlas(string atlasName, UnityEngine.Object[] packables)
        {
            string path = AtlasPath(atlasName);
            SpriteAtlas atlas = AssetDatabase.LoadAssetAtPath<SpriteAtlas>(path);
            bool isNew = atlas == null;
            if (isNew)
                atlas = new SpriteAtlas();
            else
            {
                UnityEngine.Object[] oldPackables = SpriteAtlasExtensions.GetPackables(atlas);
                if (oldPackables.Length > 0)
                    SpriteAtlasExtensions.Remove(atlas, oldPackables);
            }
            atlas.SetPackingSettings(new SpriteAtlasPackingSettings
            {
                enableRotation = false,
                enableTightPacking = false,
                padding = 8,
                blockOffset = 1
            });
            atlas.SetTextureSettings(new SpriteAtlasTextureSettings
            {
                readable = false,
                generateMipMaps = false,
                sRGB = true,
                filterMode = FilterMode.Point
            });
            atlas.SetPlatformSettings(new TextureImporterPlatformSettings
            {
                name = "Android",
                overridden = true,
                maxTextureSize = 2048,
                format = TextureImporterFormat.RGBA32,
                textureCompression = TextureImporterCompression.Uncompressed,
                compressionQuality = 100
            });
            SpriteAtlasExtensions.Add(atlas, packables);
            if (isNew)
                AssetDatabase.CreateAsset(atlas, path);
            else
                EditorUtility.SetDirty(atlas);
        }

        private static string AtlasPath(string actor) => $"{AtlasRoot}/FF_{actor}.spriteatlas";

        private static int ExpectedSpriteCount(ActorSpec actor)
        {
            if (actor.Name == "Essa") return 11 * 12;
            if (actor.Name == "Adam") return 11 * 8;
            if (actor.Name == "MarketEnforcer") return (5 * 6) + 12;
            return 6 * 6;
        }
    }
}
