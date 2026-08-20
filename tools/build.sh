#!/bin/sh
set -eu

TASK_PROJECT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
TASK_SDK_DIR=${PVSNESLIB_HOME:-/Users/essa/.codex/tools/pvsneslib-4.6.0/pvsneslib}
TASK_BUILD_DIR=$(mktemp -d /tmp/family-force-build.XXXXXX)
TASK_ROM_TEMP="$TASK_PROJECT_DIR/dist/.family-force-street-rescue.sfc.tmp.$$"
TASK_PUBLISH_ROM=0

if [ "$#" -eq 0 ]; then
  TASK_PUBLISH_ROM=1
else
  for TASK_BUILD_TARGET in "$@"; do
    case "$TASK_BUILD_TARGET" in
      all|buildActual|buildWithSummary|family_force.sfc)
        TASK_PUBLISH_ROM=1
        ;;
    esac
  done
fi

case "$TASK_BUILD_DIR" in
  /tmp/family-force-build.*) ;;
  *)
    echo "Refusing unsafe temporary build path: $TASK_BUILD_DIR" >&2
    exit 1
    ;;
esac

cleanup_build_dir() {
  rm -rf -- "$TASK_BUILD_DIR"
  rm -f -- "$TASK_ROM_TEMP"
}
trap cleanup_build_dir EXIT HUP INT TERM

if [ ! -f "$TASK_SDK_DIR/devkitsnes/snes_rules" ]; then
  echo "PVSnesLib SDK not found at: $TASK_SDK_DIR" >&2
  exit 1
fi

mkdir -p "$TASK_PROJECT_DIR/dist"

# PVSnesLib 4.6 cannot compile from a physical path containing spaces, so the
# source tree is staged into a validated no-space temporary directory.
rsync -a \
  --exclude '.git/' \
  --exclude 'dist/' \
  --exclude 'jobs/' \
  --exclude 'photos/' \
  --exclude '/family_force.sfc' \
  --exclude '/family_force.sym' \
  --exclude '/family_force.symfull' \
  --exclude '/family_force.log' \
  --exclude '/hdr.asm' \
  --exclude '/linkfile' \
  --exclude '/*.obj' \
  --exclude '/*.ps' \
  --exclude '/src/main.asm' \
  --exclude '/src/game.asm' \
  --exclude '/assets/dev/*.pic' \
  --exclude '/assets/dev/*.map' \
  --exclude '/assets/dev/*.pal' \
  --exclude '/assets/dev/*.inc' \
  --exclude '/assets/dev/*_data.as' \
  --exclude '/audio/soundbank.asm' \
  --exclude '/audio/soundbank.h' \
  --exclude '/audio/soundbank.bnk' \
  --exclude '/audio/soundbank.obj' \
  "$TASK_PROJECT_DIR/" "$TASK_BUILD_DIR/"

export PVSNESLIB_HOME="$TASK_SDK_DIR"
export PATH="/opt/homebrew/opt/gnu-sed/libexec/gnubin:$PATH"

make -C "$TASK_BUILD_DIR" "$@"

if [ "$TASK_PUBLISH_ROM" -eq 1 ]; then
  if [ ! -f "$TASK_BUILD_DIR/family_force.sfc" ]; then
    echo "Build target did not produce family_force.sfc" >&2
    exit 1
  fi
  TASK_ROM_SIZE=$(wc -c < "$TASK_BUILD_DIR/family_force.sfc" | tr -d ' ')
  if [ "$TASK_ROM_SIZE" -ne 4194304 ]; then
    echo "Unexpected ROM size: $TASK_ROM_SIZE bytes" >&2
    exit 1
  fi

  cp -f "$TASK_BUILD_DIR/family_force.sfc" "$TASK_ROM_TEMP"
  mv -f "$TASK_ROM_TEMP" "$TASK_PROJECT_DIR/dist/family-force-street-rescue.sfc"
  if [ -f "$TASK_BUILD_DIR/family_force.sym" ]; then
    cp -f "$TASK_BUILD_DIR/family_force.sym" "$TASK_PROJECT_DIR/dist/family-force-street-rescue.sym"
  fi
  if [ -f "$TASK_BUILD_DIR/family_force.symfull" ]; then
    cp -f "$TASK_BUILD_DIR/family_force.symfull" "$TASK_PROJECT_DIR/dist/family-force-street-rescue.symfull"
  fi
  if [ -f "$TASK_BUILD_DIR/family_force.log" ]; then
    cp -f "$TASK_BUILD_DIR/family_force.log" "$TASK_PROJECT_DIR/dist/family-force-street-rescue.log"
  fi
  if [ -f "$TASK_BUILD_DIR/hdr.asm" ]; then
    cp -f "$TASK_BUILD_DIR/hdr.asm" "$TASK_PROJECT_DIR/dist/generated-hdr.asm"
  fi
  echo "ROM: $TASK_PROJECT_DIR/dist/family-force-street-rescue.sfc"
fi
