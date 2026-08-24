#!/bin/sh
# Debug-only emulator soak for the complete fourteen-zone route. The production
# APK ignores familyforce.fullStageTest because GameView guards it by
# BuildConfig.DEBUG.
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PROJECT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
export JAVA_HOME=${JAVA_HOME:-/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home}
export ANDROID_HOME=${ANDROID_HOME:-/Users/essa/Library/Android/sdk}
export PATH="$ANDROID_HOME/platform-tools:$PATH"

if ! adb get-state >/dev/null 2>&1; then
    echo "SKIP: no Android emulator or device connected"
    exit 0
fi

cd "$PROJECT"
./gradlew :app:assembleDebug >/dev/null
APK=app/build/outputs/apk/debug/app-debug.apk
PACKAGE=com.familyforce.neonstreets.familycurrent.debug
ACTIVITY="$PACKAGE/com.familyforce.neonstreets.MainActivity"
REPORT=app/build/reports/full-stage-runtime
mkdir -p "$REPORT"

adb install -r "$APK" >/dev/null
adb shell pm clear "$PACKAGE" >/dev/null
adb logcat -c
adb shell wm size 1920x1080 >/dev/null
adb shell am start -W -n "$ACTIVITY" --ez familyforce.fullStageTest true \
    > "$REPORT/launch.txt"
sleep 1
# TITLE -> MENU -> 1 PLAYER -> SELECT -> INTRO -> PLAY.
adb shell input keyevent 23
sleep 1
adb shell input keyevent 23
sleep 1
adb shell input keyevent 103
adb shell input keyevent 23
sleep 1
adb shell input keyevent 23
# Four spectator-boss promotions make the fourteen-zone route longer than the
# legacy nine-zone soak. Keep this below one minute while allowing every boss
# to move from WATCHING to FIGHTING before the next zone.
sleep 48

test -n "$(adb shell pidof "$PACKAGE")"
adb shell dumpsys meminfo "$PACKAGE" > "$REPORT/meminfo.txt"
adb shell dumpsys gfxinfo "$PACKAGE" framestats > "$REPORT/framestats.txt"
adb shell screencap -p /sdcard/family-force-full-stage.png
adb pull /sdcard/family-force-full-stage.png "$REPORT/final.png" >/dev/null
adb shell run-as "$PACKAGE" cat shared_prefs/family_force_runtime_diagnostics.xml \
    > "$REPORT/runtime-diagnostics.xml"

if adb logcat -d -t 5000 | grep -E \
    "FATAL EXCEPTION|ANR in $PACKAGE|OutOfMemoryError|lowmemorykiller.*$PACKAGE" \
    > "$REPORT/failure.txt"; then
    echo "FAIL: Android runtime failure detected" >&2
    exit 1
fi
if ! grep -q "STAGE_COMPLETE" "$REPORT/runtime-diagnostics.xml"; then
    echo "FAIL: fourteen-zone test did not reach results" >&2
    exit 1
fi
adb shell wm size reset >/dev/null
printf 'status=PASS\nroute=zones-1-through-14\nmode=debug-only\n' > "$REPORT/summary.txt"
echo "PASS: full fourteen-zone Android TV route completed ($REPORT)"
