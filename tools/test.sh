#!/bin/sh
set -eu

TASK_PROJECT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
TASK_SIM_BIN=$(mktemp /tmp/family-force-sim-test.XXXXXX)
TASK_ROM="$TASK_PROJECT_DIR/dist/family-force-street-rescue.sfc"
TASK_MESEN="/Applications/Mesen.app/Contents/MacOS/Mesen"

cd "$TASK_PROJECT_DIR"

clang -std=c89 -Wall -Wextra -Werror -pedantic -Isrc \
  src/game.c tests/sim_test.c -o "$TASK_SIM_BIN"
"$TASK_SIM_BIN"

python3 -m unittest discover -s tests -p 'audio*.py' -v
./tools/build.sh
python3 tools/validate_rom.py "$TASK_ROM"

if [ -x "$TASK_MESEN" ]; then
  "$TASK_MESEN" --testRunner --timeout=20 tests/mesen_smoke.lua "$TASK_ROM"
else
  echo "Mesen not installed; emulator smoke test skipped" >&2
fi
