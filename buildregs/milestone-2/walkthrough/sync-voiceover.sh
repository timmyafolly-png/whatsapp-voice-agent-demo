#!/usr/bin/env bash
# Split a single-take voiceover on its pauses and report each section's length.
# Usage: ./sync-voiceover.sh voiceover.m4a
# Output feeds the HOLD array in record.js so slides match the narration.
set -euo pipefail
IN="${1:?usage: sync-voiceover.sh <audio file>}"
FF=$(python3 -c "import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())")
echo "== silence map (gaps of 1.2s+ below -32dB) =="
"$FF" -hide_banner -i "$IN" -af "silencedetect=noise=-32dB:d=1.2" -f null - 2>&1 \
  | grep -E "silence_(start|end)" || echo "no gaps found — pauses may be too short or the room too noisy"
echo
echo "== total duration =="
"$FF" -hide_banner -i "$IN" 2>&1 | grep Duration
