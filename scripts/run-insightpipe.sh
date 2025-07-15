#!/bin/bash

SHARE="smb://crowunas@192.168.10.211/wildlife"
MOUNTPOINT="/Volumes/wildlife"
LOGFILE="/tmp/insightpipe.debug.log"
MAX_WAIT=30
WAIT_INTERVAL=2

echo "$(date) — Launching mount attempt for $SHARE" >> "$LOGFILE"
open "$SHARE"

# Wait for mount to appear
elapsed=0
while [ ! -d "$MOUNTPOINT" ] && [ "$elapsed" -lt "$MAX_WAIT" ]; do
    sleep "$WAIT_INTERVAL"
    elapsed=$((elapsed + WAIT_INTERVAL))
done

if [ ! -d "$MOUNTPOINT" ]; then
    echo "$(date) — SMB mount failed to appear within $MAX_WAIT seconds" >> /tmp/insightpipe.err.log
    exit 1
fi

echo "$(date) — SMB share available at $MOUNTPOINT" >> "$LOGFILE"

# Continue to activate venv and run InsightPipe...

# --- Python Environment and Execution ---
echo "$(date) — Activating virtual environment" >> "$LOGFILE"
source /Users/crow/projects/insightpipe/venv-insight/bin/activate

echo "$(date) — Launching InsightPipe with config_detection.yaml" >> "$LOGFILE"
python3 /Users/crow/projects/insightpipe/insightpipe.py \
  --config /Users/crow/projects/insightpipe/config_detection.yaml \
  --no_keywords --watch

echo "$(date) — InsightPipe exited" >> "$LOGFILE"
