#!/bin/sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
ANDROID_PROJECT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
WORKSPACE=$(CDPATH= cd -- "$ANDROID_PROJECT/.." && pwd)

export JAVA_HOME=${JAVA_HOME:-/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home}
export ANDROID_HOME=${ANDROID_HOME:-/Users/essa/Library/Android/sdk}
export ANDROID_SDK_ROOT=${ANDROID_SDK_ROOT:-$ANDROID_HOME}

python3 "$SCRIPT_DIR/validate_assets.py"
"$ANDROID_PROJECT/gradlew" --no-daemon -p "$ANDROID_PROJECT" :app:assembleDebug

SOURCE_APK="$ANDROID_PROJECT/app/build/outputs/apk/debug/app-debug.apk"
OUTPUT_APK="$WORKSPACE/dist/family-force-neon-streets.apk"
test -f "$SOURCE_APK"
mkdir -p "$WORKSPACE/dist"
cp "$SOURCE_APK" "$OUTPUT_APK"

"$ANDROID_HOME/build-tools/34.0.0/apksigner" verify --verbose "$OUTPUT_APK"
echo "APK: $OUTPUT_APK"
shasum -a 256 "$OUTPUT_APK"
