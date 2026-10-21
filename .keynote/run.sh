#!/usr/bin/env bash
# Fetch the GTC Berlin 2026 keynote transcript once the stream has ended.
# Usage: run.sh OUT_DIR [VIDEO_ID] [MINUTES]   (idempotent: safe to re-run into the same OUT_DIR)
#   NO_WHISPER=1 skips the audio/Whisper pass.
set -u
OUT=${1:?out dir}; ID=${2:-PvFjbPYEOZI}; MINUTES=${3:-100}
HERE=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$OUT"; cd "$OUT"
log() { echo "$(date -u +%H:%M:%S) $*" | tee -a status.log; }
python3 -c "import faster_whisper, yt_dlp_ejs" 2>/dev/null || pip install -q -U "yt-dlp[default]" faster-whisper
export PATH="/opt/node22/bin:$PATH"
CLIENTS=(default default web_embedded)
yt() {  # rotate player clients: the datacenter IP gets intermittent bot checks
  local c=${CLIENTS[$((RANDOM % ${#CLIENTS[@]}))]}
  timeout 300 yt-dlp --js-runtimes node --extractor-args "youtube:player_client=$c" "$@"
}

# NVIDIA sometimes restarts a stream under a new ID or re-uploads it as a "Full Replay";
# if the expected ID stops resolving, take the newest matching keynote from the channel.
find_id() {
  for tab in streams videos; do
    timeout 120 yt-dlp --flat-playlist --playlist-end 15 --print "%(id)s|%(title)s" \
      "https://www.youtube.com/@NVIDIA/$tab" 2>/dev/null |
      grep -i "berlin" | grep -i "keynote" | grep -vi "pregame" | head -1 | cut -d'|' -f1
  done | head -1
}

deadline=$(( $(date +%s) + MINUTES * 60 ))
if [ ! -s transcript-captions.txt ]; then
  i=0
  while [ "$(date +%s)" -lt "$deadline" ]; do
    i=$((i + 1))
    if [ $((i % 10)) -eq 0 ]; then
      new=$(find_id); [ -n "$new" ] && [ "$new" != "$ID" ] && { log "switching video $ID -> $new"; ID=$new; rm -f keynote.*; }
    fi
    URL="https://www.youtube.com/watch?v=$ID"
    # human-made English captions first, then YouTube's auto captions
    yt --skip-download --ignore-no-formats-error --write-subs --sub-langs "en,en-US,en-GB" --sub-format vtt -o "keynote.manual.%(live_status)s.%(ext)s" "$URL" > fetch.log 2>&1
    yt --skip-download --ignore-no-formats-error --write-auto-subs --sub-langs "en-orig,en" --sub-format vtt -o "keynote.auto.%(live_status)s.%(ext)s" "$URL" >> fetch.log 2>&1
    f=$(ls keynote.manual.{was_live,not_live}.en*.vtt keynote.auto.{was_live,not_live}.en-orig.vtt keynote.auto.{was_live,not_live}.en.vtt 2>/dev/null | head -1)  # never a partial capture of a still-live stream
    if [ -n "$f" ] && python3 -I "$HERE/vtt2txt.py" "$f" > transcript-captions.tmp && [ "$(wc -w < transcript-captions.tmp)" -gt 2000 ]; then
      mv transcript-captions.tmp transcript-captions.txt; echo "$ID" > video_id
      log "captions OK: $f ($(wc -w < transcript-captions.txt) words, video $ID)"; break
    fi
    log "attempt $i ($ID): $(grep -m1 -oE 'ERROR.{0,90}|live event will begin.{0,40}' fetch.log || echo 'no captions yet (still live or processing)')"
    sleep 120  # gentler polling: 45s got the IP rate-limited (HTTP 429)
  done
  [ -s transcript-captions.txt ] || { log "CAPTIONS NOT AVAILABLE YET after $MINUTES min"; exit 2; }
fi

# bonus: Whisper transcript from audio, if YouTube lets the audio through
[ -n "${NO_WHISPER:-}" ] && exit 0
[ -s transcript-whisper.txt ] && exit 0
ID=$(cat video_id 2>/dev/null || echo "$ID")
for i in 1 2 3; do
  yt -f "233/234/bestaudio" -o "audio.%(ext)s" "https://www.youtube.com/watch?v=$ID" >/dev/null 2>&1 && break; sleep 30
done
a=$(ls audio.* 2>/dev/null | grep -vE '\.(part|ytdl)$' | head -1)
[ -n "$a" ] || { log "audio blocked; captions only"; exit 0; }
log "audio OK, running Whisper"
python3 -I - "$a" <<'PY'
import sys
from faster_whisper import WhisperModel
segs, _ = WhisperModel("small.en", device="cpu", compute_type="int8", cpu_threads=4).transcribe(sys.argv[1], vad_filter=True)
with open("transcript-whisper.tmp", "w") as f:
    for s in segs:
        t = int(s.start); f.write(f"[{t//3600}:{t%3600//60:02d}:{t%60:02d}] {s.text.strip()}\n"); f.flush()
PY
mv transcript-whisper.tmp transcript-whisper.txt && log "whisper done"
