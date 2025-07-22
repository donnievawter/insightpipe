#!/bin/bash


LOGFILE="/tmp/insightpipe-wildlife.debug.log"
MAX_WAIT=30
WAIT_INTERVAL=2

# Continue to activate venv and run InsightPipe...

# --- Python Environment and Execution ---
echo "$(date) — Activating virtual environment" >> "$LOGFILE"
source /Users/crow/projects/insightpipe/venv-insight/bin/activate

echo "$(date) — Launching InsightPipe with config_detection.yaml" >> "$LOGFILE"
python3 /Users/crow/projects/insightpipe/insightpipe.py \
  --config /Users/crow/projects/insightpipe/config_detection.yaml \
  --watch

echo "$(date) — InsightPipe exited" >> "$LOGFILE"
