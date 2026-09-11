"""Build a dependency-free AAR with Unity's installed Android JDK/SDK."""
from pathlib import Path
import subprocess, tempfile, zipfile

ROOT = Path(__file__).resolve().parents[1]
ANDROID = Path('/Applications/Unity/Hub/Editor/6000.3.22f1/PlaybackEngines/AndroidPlayer')
SOURCE = ROOT / 'android-updater'
DEST = ROOT / 'Assets/Plugins/Android/FamilyForceUpdater.aar'
DEST.parent.mkdir(parents=True, exist_ok=True)
with tempfile.TemporaryDirectory(prefix='ff-updater-') as tmp:
    classes = Path(tmp) / 'classes'
    classes.mkdir()
    subprocess.run([str(ANDROID/'OpenJDK/bin/javac'), '-source', '8', '-target', '8',
                    '-classpath', str(ANDROID/'SDK/platforms/android-36/android.jar'),
                    '-d', str(classes), *map(str, SOURCE.glob('src/**/*.java'))], check=True)
    jar = Path(tmp) / 'classes.jar'
    subprocess.run([str(ANDROID/'OpenJDK/bin/jar'), 'cf', str(jar), '-C', str(classes), '.'], check=True)
    with zipfile.ZipFile(DEST, 'w', zipfile.ZIP_DEFLATED) as aar:
        aar.write(jar, 'classes.jar')
        aar.write(SOURCE/'AndroidManifest.xml', 'AndroidManifest.xml')
        aar.writestr('proguard.txt', '-keep class com.familyforce.updates.** { *; }\n')
print(DEST)
