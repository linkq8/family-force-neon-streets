# Family Force audio starter pack

This directory contains an original, procedural audio set for PVSnesLib
4.6.0. No third-party recordings, samples, model outputs, or existing
melodies were used. `tools/generate_audio.py` is the complete source of every
waveform and note event.

| Asset | Source format | SNES format | Intended use |
|---|---:|---:|---|
| `stage_loop.it` | Impulse Tracker 2.14 | `smconv` soundbank | 12.8-second, 150 BPM looping street-stage theme |
| `punch.wav` | mono PCM16, 8 kHz | `punch.brr` | light/heavy hit feedback |
| `jump.wav` | mono PCM16, 8 kHz | `jump.brr` | jump takeoff |
| `damage.wav` | mono PCM16, 8 kHz | `damage.brr` | player damage |
| `pickup.wav` | mono PCM16, 8 kHz | `pickup.brr` | health/score pickup |
| `confirm.wav` | mono PCM16, 8 kHz | `confirm.brr` | menu confirm/start |
| `victory.wav` | mono PCM16, 8 kHz | `victory.brr` | stage clear |

The music deliberately uses only channels 1–6. Channels 7 and 8 remain free;
PVSnesLib/SNESMOD can therefore use its effects voice without erasing an
important musical line. Its five embedded samples total far less than the
SNES audio RAM budget, and every loop point is aligned to 16 samples.

Regenerate and verify against the pinned SDK:

```sh
python3 tools/generate_audio.py \
  --pvsneslib-home /Users/essa/.codex/tools/pvsneslib-4.6.0/pvsneslib
python3 -m unittest discover -s tests -p 'audio*.py' -v
```

The standalone BRR effects use PVSnesLib pitch `4` (8 kHz). The largest is
`victory.brr` at 3,465 bytes, so `spcAllocateSoundRegion(16)` reserves a safe
4 KiB streaming region.

