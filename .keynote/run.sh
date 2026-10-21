#!/usr/bin/env bash
# Fetch the GTC Berlin 2026 keynote transcript once the stream has ended.
# Usage: run.sh OUT_DIR [VIDEO_ID]
set -u
OUT=${1:?out dir}; ID=${2:-PvFjbPYEOZI}
URL="https://www.youtube.com/watch?v=$ID"
HERE=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$OUT"; cd "$OUT"
python3 -c "import faster_whisper, yt_dlp_ejs" 2>/dev/null || pip install -q -U "yt-dlp[default]" faster-whisper
YT="yt-dlp --js-runtimes node"

# 1) captions: YouTube bot-checks this IP intermittently, and VOD captions can lag the stream end
for i in $(seq 1 240); do
  $YT --skip-download --write-auto-subs --write-subs --sub-langs "en-orig,en" --sub-format vtt -o "keynote.%(ext)s" "$URL" > fetch.log 2>&1
  f=$(ls keynote.en-orig.vtt keynote.en.vtt 2>/dev/null | head -1)
  if [ -n "$f" ]; then python3 -I "$HERE/vtt2txt.py" "$f" > transcript-captions.txt; echo "captions OK: $f"; break; fi
  echo "attempt $i: $(grep -m1 ERROR fetch.log | cut -c1-120)"
  sleep 45
done

# 2) bonus: Whisper transcript from audio, if YouTube lets the audio through
for i in 1 2 3; do
  timeout 1800 $YT -f "233/234/bestaudio" -o "audio.%(ext)s" "$URL" >/dev/null 2>&1 && break; sleep 30
done
a=$(ls audio.* 2>/dev/null | head -1)
if [ -n "$a" ]; then
  python3 -I - "$a" <<'PY'
import sys
from faster_whisper import WhisperModel
segs, _ = WhisperModel("small.en", device="cpu", compute_type="int8", cpu_threads=4).transcribe(sys.argv[1], vad_filter=True)
with open("transcript-whisper.txt", "w") as f:
    for s in segs:
        t = int(s.start); f.write(f"[{t//3600}:{t%3600//60:02d}:{t%60:02d}] {s.text.strip()}\n"); f.flush()
PY
  echo "whisper done"
else
  echo "audio blocked; captions only"
fi
ls -la
