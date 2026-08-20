#!/bin/sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
ANDROID_PROJECT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
WORKSPACE=$(CDPATH= cd -- "$ANDROID_PROJECT/.." && pwd)

export ANDROID_HOME=${ANDROID_HOME:-/Users/essa/Library/Android/sdk}
export PATH="$ANDROID_HOME/platform-tools:$PATH"

"$SCRIPT_DIR/build_apk.sh"
APK="$WORKSPACE/dist/family-force-neon-streets.apk"
PACKAGE="com.familyforce.neonstreets.debug"
ACTIVITY="com.familyforce.neonstreets.MainActivity"

if ! adb get-state >/dev/null 2>&1; then
    echo "No Android device/emulator is connected; build and signature checks passed."
    exit 0
fi

adb install -r "$APK" >/dev/null
adb logcat -c
adb shell am start -S -n "$PACKAGE/$ACTIVITY" >/dev/null

attempt=0
while [ "$attempt" -lt 20 ]; do
    if adb shell pidof "$PACKAGE" | grep -q '[0-9]'; then
        break
    fi
    attempt=$((attempt + 1))
done

test "$attempt" -lt 20
if adb logcat -d -t 500 | grep -E 'FATAL EXCEPTION|ANR in com\.familyforce\.neonstreets' >/dev/null; then
    echo "Android runtime failure detected" >&2
    adb logcat -d -t 500 >&2
    exit 1
fi

echo "Android install/start smoke test passed on $(adb shell getprop ro.build.version.release)."
