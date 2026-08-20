#!/bin/sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
ANDROID_PROJECT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
WORKSPACE=$(CDPATH= cd -- "$ANDROID_PROJECT/.." && pwd)
PACK=${1:-"$WORKSPACE/customers/family-current"}
PACK=$(CDPATH= cd -- "$PACK" && pwd)

export JAVA_HOME=${JAVA_HOME:-/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home}
export ANDROID_HOME=${ANDROID_HOME:-/Users/essa/Library/Android/sdk}
export PATH="$ANDROID_HOME/platform-tools:$PATH"

"$SCRIPT_DIR/test_controller_compat.sh"
python3 "$SCRIPT_DIR/test_combat_companion_contract.py"
"$SCRIPT_DIR/build_customer_apk.sh" "$PACK" draft
ORDER_ID=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["orderId"])' "$PACK/customer.json")
SAFE_ID=$(printf '%s' "$ORDER_ID" | tr -cd 'a-z0-9')
PACKAGE="com.familyforce.neonstreets.event.$SAFE_ID"
APK="$WORKSPACE/dist/customers/$ORDER_ID/family-force-$ORDER_ID.apk"
REPORT_DIR="$WORKSPACE/dist/customers/$ORDER_ID/qa"
mkdir -p "$REPORT_DIR"

python3 "$SCRIPT_DIR/test_tv_selection_memory_contract.py"
python3 "$SCRIPT_DIR/test_tv_encounter_memory_contract.py"
python3 "$SCRIPT_DIR/test_weapon_pickup_contract.py"
python3 "$SCRIPT_DIR/test_enemy_attack_tokens_contract.py"
python3 "$SCRIPT_DIR/test_move_specs_contract.py"
python3 "$SCRIPT_DIR/test_checkpoint_contract.py"
python3 "$SCRIPT_DIR/test_audio_lifecycle_contract.py"
python3 "$SCRIPT_DIR/test_encounter_gate_contract.py"
python3 "$SCRIPT_DIR/test_runtime_diagnostics_contract.py"

python3 "$SCRIPT_DIR/verify_customer_apk.py" --apk "$APK" --pack "$PACK" \
    --aapt "$ANDROID_HOME/build-tools/34.0.0/aapt" \
    --report "$REPORT_DIR/apk-verification.json"

if ! adb get-state >/dev/null 2>&1; then
    echo "No emulator/device connected; archive, signature, assets, and metadata passed."
    exit 0
fi

# Install twice: first install and the exact update path customers will use.
adb install -r "$APK" >/dev/null
adb install -r "$APK" >/dev/null
adb logcat -c

run_profile() {
    label=$1
    width=$2
    height=$3
    adb shell wm size "${width}x${height}" >/dev/null
    adb shell am force-stop "$PACKAGE"
    adb shell am start -W -n "$PACKAGE/com.familyforce.neonstreets.MainActivity" \
        > "$REPORT_DIR/${label}-launch.txt"
    sleep 1
    test -n "$(adb shell pidof "$PACKAGE")"
    # TV remote/controller-compatible navigation signals. They must never crash a menu.
    adb shell input keyevent 20
    adb shell input keyevent 22
    adb shell input keyevent 23
    adb shell input keyevent 4
    sleep 1
    adb shell dumpsys meminfo "$PACKAGE" > "$REPORT_DIR/${label}-meminfo.txt"
    adb shell dumpsys gfxinfo "$PACKAGE" framestats > "$REPORT_DIR/${label}-framestats.txt"
    if adb logcat -d -t 1500 | grep -E "FATAL EXCEPTION|ANR in $PACKAGE|OutOfMemoryError" \
            > "$REPORT_DIR/${label}-failure.txt"; then
        adb shell wm size reset >/dev/null
        echo "Runtime failure in $label" >&2
        exit 1
    fi
}

run_profile phone 640 360
run_profile ultrawide 720 320
run_profile fold 1080 928
run_profile android-tv 1920 1080

# Reproduce the complete Android TV remote path. The old smoke test only moved
# around the menu and could not catch selection/start crashes or companion
# cycling failures.
run_tv_two_player_flow() {
    adb shell wm size 1920x1080 >/dev/null
    adb shell am force-stop "$PACKAGE"
    adb logcat -c
    adb shell am start -W -n "$PACKAGE/com.familyforce.neonstreets.MainActivity" \
        > "$REPORT_DIR/android-tv-remote-flow-launch.txt"
    sleep 1
    # TITLE -> MENU -> 2 PLAYERS -> SELECT. CONTINUE and 1 PLAYER now precede it.
    adb shell input keyevent 23
    adb shell input keyevent 20
    adb shell input keyevent 20
    adb shell input keyevent 23
    sleep 1
    test -n "$(adb shell pidof "$PACKAGE")"
    # Cycle each player's companion with R1, then lock both players and enter PLAY.
    adb shell input keyevent 103
    adb shell input keyevent 23
    adb shell input keyevent 103
    adb shell input keyevent 23
    sleep 1
    test -n "$(adb shell pidof "$PACKAGE")"
    adb shell input keyevent 23
    sleep 3
    test -n "$(adb shell pidof "$PACKAGE")"
    adb shell dumpsys meminfo "$PACKAGE" > "$REPORT_DIR/android-tv-remote-flow-meminfo.txt"
    adb shell dumpsys gfxinfo "$PACKAGE" framestats \
        > "$REPORT_DIR/android-tv-remote-flow-framestats.txt"
    if adb logcat -d -t 4000 | grep -E \
            "FATAL EXCEPTION|ANR in $PACKAGE|OutOfMemoryError|lowmemorykiller.*$PACKAGE" \
            > "$REPORT_DIR/android-tv-remote-flow-failure.txt"; then
        echo "Runtime failure in complete Android TV remote flow" >&2
        exit 1
    fi
}

run_tv_two_player_flow
adb shell wm size reset >/dev/null

printf 'status=PASS\npackage=%s\nprofiles=phone,ultrawide,fold,android-tv,android-tv-remote-two-player\n' "$PACKAGE" \
    > "$REPORT_DIR/runtime-summary.txt"
echo "Customer release runtime QA passed: $REPORT_DIR"
