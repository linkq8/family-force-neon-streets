using UnityEditor;
using UnityEngine;

namespace FamilyForce.Unity.Editor
{
    public static class Controller226Build
    {
        public static void ConfigureAxes()
        {
            var so=new SerializedObject(AssetDatabase.LoadAllAssetsAtPath("ProjectSettings/InputManager.asset")[0]);
            var axes=so.FindProperty("m_Axes");
            string[] names={"X","Y"};int[] indices={0,1};
            for(int player=1;player<=2;player++)for(int axis=0;axis<2;axis++)
            {
                string name=$"FF_P{player}_{names[axis]}";SerializedProperty entry=null;
                for(int i=0;i<axes.arraySize;i++){var e=axes.GetArrayElementAtIndex(i);if(e.FindPropertyRelative("m_Name").stringValue==name){entry=e;break;}}
                if(entry==null){axes.InsertArrayElementAtIndex(axes.arraySize);entry=axes.GetArrayElementAtIndex(axes.arraySize-1);}
                entry.FindPropertyRelative("m_Name").stringValue=name;
                foreach(string key in new[]{"descriptiveName","descriptiveNegativeName","negativeButton","positiveButton","altNegativeButton","altPositiveButton"})entry.FindPropertyRelative(key).stringValue="";
                entry.FindPropertyRelative("type").intValue=2;entry.FindPropertyRelative("axis").intValue=indices[axis];entry.FindPropertyRelative("joyNum").intValue=player;
                entry.FindPropertyRelative("gravity").floatValue=0;entry.FindPropertyRelative("sensitivity").floatValue=1;
                entry.FindPropertyRelative("dead").floatValue=.15f;entry.FindPropertyRelative("snap").boolValue=false;entry.FindPropertyRelative("invert").boolValue=axis==1||axis==3;
            }
            so.ApplyModifiedPropertiesWithoutUndo();AssetDatabase.SaveAssets();
        }
    }
}
