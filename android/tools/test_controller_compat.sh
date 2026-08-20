#!/bin/sh
set -eu

PROJECT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
ANDROID_JAR="${ANDROID_HOME:-${ANDROID_SDK_ROOT:-$HOME/Library/Android/sdk}}/platforms/android-34/android.jar"
JAVA_BIN="${JAVA_HOME:+$JAVA_HOME/bin/}java"
JAVAC_BIN="${JAVA_HOME:+$JAVA_HOME/bin/}javac"

if [ ! -f "$ANDROID_JAR" ]; then
    echo "Missing Android 34 platform jar: $ANDROID_JAR" >&2
    exit 1
fi
if ! command -v "$JAVA_BIN" >/dev/null 2>&1 || ! command -v "$JAVAC_BIN" >/dev/null 2>&1; then
    echo "Java and javac are required (set JAVA_HOME to JDK 17)." >&2
    exit 1
fi

BUILD_DIR=$(mktemp -d "${TMPDIR:-/tmp}/family-force-controller-test.XXXXXX")
trap 'rm -rf "$BUILD_DIR"' EXIT HUP INT TERM

"$JAVAC_BIN" -cp "$ANDROID_JAR" -d "$BUILD_DIR" \
    "$PROJECT_DIR/app/src/main/java/com/familyforce/neonstreets/ControllerCompat.java" \
    "$PROJECT_DIR/tests/ControllerCompatMain.java"
"$JAVA_BIN" -cp "$BUILD_DIR:$ANDROID_JAR" \
    com.familyforce.neonstreets.ControllerCompatMain
