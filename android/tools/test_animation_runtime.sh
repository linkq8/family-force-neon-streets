#!/bin/sh
# Emulator QA for animation actions and responsive/Fold display profiles.
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
ANDROID_PROJECT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
WORKSPACE=$(CDPATH= cd -- "$ANDROID_PROJECT/.." && pwd)

export ANDROID_HOME=${ANDROID_HOME:-/Users/essa/Library/Android/sdk}
export PATH="$ANDROID_HOME/platform-tools:$PATH"

APK=${1:-"$WORKSPACE/dist/family-force-neon-streets.apk"}
PACKAGE=com.familyforce.neonstreets.debug
ACTIVITY=com.familyforce.neonstreets.MainActivity
REPORT_DIR=${ANIMATION_QA_REPORT_DIR:-"$ANDROID_PROJECT/app/build/reports/animation-runtime"}

test -f "$APK"
adb get-state >/dev/null 2>&1 || {
    echo "Animation runtime QA requires one connected Android emulator." >&2
    exit 2
}

size_state=$(adb shell wm size | tr -d '\r')
saved_override=$(printf '%s\n' "$size_state" | sed -n 's/^Override size: //p')

restore_display() {
    if [ -n "$saved_override" ]; then
        adb shell wm size "$saved_override" >/dev/null 2>&1 || true
    else
        adb shell wm size reset >/dev/null 2>&1 || true
    fi
}
trap restore_display EXIT HUP INT TERM

mkdir -p "$REPORT_DIR"
adb install -r "$APK" >/dev/null
adb logcat -c

wait_for_focus() {
    attempt=0
    while [ "$attempt" -lt 50 ]; do
        if adb shell dumpsys window 2>/dev/null \
                | grep -q "mCurrentFocus=.*$PACKAGE/$ACTIVITY"; then
            return 0
        fi
        attempt=$((attempt + 1))
        sleep 0.1
    done
    echo "Timed out waiting for $PACKAGE/$ACTIVITY" >&2
    return 1
}

launch_game() {
    hero_index=$1
    adb shell am force-stop "$PACKAGE"
    adb shell am start -S -n "$PACKAGE/$ACTIVITY" >/dev/null
    wait_for_focus
    sleep 0.35
    # TITLE -> MENU -> SELECT, choose hero, SELECT -> INTRO -> PLAY.
    adb shell input keyevent 66
    sleep 0.15
    adb shell input keyevent 66
    sleep 0.15
    selected=0
    while [ "$selected" -lt "$hero_index" ]; do
        adb shell input keyevent 22
        selected=$((selected + 1))
    done
    adb shell input keyevent 66
    sleep 0.15
    adb shell input keyevent 66
    sleep 0.4
    # Expose atlas row/frame in the in-game debug overlay and fill meters.
    adb shell input keyevent 133
    adb shell input keyevent 134
}

capture() {
    name=$1
    adb exec-out screencap -p > "$REPORT_DIR/$name.png"
}

capture_action_pair() {
    label=$1
    keycode=$2
    adb shell input keyevent "$keycode"
    sleep 0.05
    capture "compact_essa_${label}_early"
    sleep 0.15
    capture "compact_essa_${label}_late"
    sleep 0.65
}

run_profile() {
    label=$1
    override=$2
    expected=$3
    adb shell wm size "$override" >/dev/null
    launch_game 0
    capture "${label}_gameplay"
    actual=$(python3 - "$REPORT_DIR/${label}_gameplay.png" <<'PY'
from pathlib import Path
import sys
from PIL import Image
with Image.open(Path(sys.argv[1])) as image:
    print(f"{image.width}x{image.height}")
PY
)
    if [ "$actual" != "$expected" ]; then
        echo "$label screenshot is $actual; expected $expected" >&2
        exit 1
    fi
    echo "PASS $label display profile: $actual"
}

# Compact 16:9 profile: capture two points in every requested player action.
adb shell wm size 360x640 >/dev/null
launch_game 0
capture "compact_essa_idle"
adb shell input keyevent --longpress 22 >/dev/null &
walk_pid=$!
sleep 0.2
capture "compact_essa_walk"
wait "$walk_pid"
sleep 0.3
capture_action_pair punch 54
capture_action_pair kick 52
capture_action_pair heavy_punch 31
capture_action_pair heavy_kick 50
capture_action_pair jump 62
adb shell input keyevent 134
capture_action_pair special 33
adb shell input keyevent 134
capture_action_pair link 45

# Prove that each character atlas can be selected and decoded by the runtime.
hero_index=1
for hero_name in adam shaikha sulaiman; do
    launch_game "$hero_index"
    capture "compact_${hero_name}_idle"
    adb shell input keyevent 54
    sleep 0.12
    capture "compact_${hero_name}_punch"
    hero_index=$((hero_index + 1))
done

run_profile compact 360x640 640x360
run_profile ultrawide 320x720 720x320
run_profile fold6_inner 928x1080 1080x928

adb shell dumpsys gfxinfo "$PACKAGE" framestats > "$REPORT_DIR/fold6_framestats.txt"
adb logcat -d -t 1200 > "$REPORT_DIR/logcat.txt"
if grep -E "FATAL EXCEPTION|ANR in com\.familyforce\.neonstreets" \
        "$REPORT_DIR/logcat.txt" >/dev/null; then
    echo "Android runtime failure detected" >&2
    exit 1
fi

python3 - "$REPORT_DIR" <<'PY'
"""Require visible hero-region changes between early/late action captures."""
from pathlib import Path
import sys
from PIL import Image, ImageChops

root = Path(sys.argv[1])
for early in sorted(root.glob("compact_essa_*_early.png")):
    late = Path(str(early).replace("_early.png", "_late.png"))
    with Image.open(early) as first_source, Image.open(late) as second_source:
        # In the 640x360 compact profile the player starts at x=185, base y=278.
        box = (78, 58, 300, 310)
        first = first_source.convert("RGB").crop(box)
        second = second_source.convert("RGB").crop(box)
    histogram = ImageChops.difference(first, second).convert("L").histogram()
    changed = sum(histogram[1:]) / (first.width * first.height)
    if changed < 0.003:
        raise SystemExit(
            f"{early.stem}: hero/action region barely changed ({changed:.3%})"
        )
    print(f"PASS {early.stem}: visible region change {changed:.2%}")
PY

echo "Animation/Fold runtime QA passed. Reports: $REPORT_DIR"
