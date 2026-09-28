#!/usr/bin/env bash
# Re-encode the captured WebM to H.264 MP4.
# Playwright's bundled ffmpeg can only write VP8, so this uses the static build
# that ships with the imageio-ffmpeg pip package, which carries libx264 and aac.
#   pip install imageio-ffmpeg
set -euo pipefail
FF=$(python3 -c "import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())")
"$FF" -y -i buildregs-walkthrough.webm \
  -c:v libx264 -preset slow -crf 20 -pix_fmt yuv420p -vf fps=25 \
  -movflags +faststart buildregs-walkthrough.mp4
