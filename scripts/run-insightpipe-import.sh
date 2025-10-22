#!/bin/bash


LOGFILE="/tmp/insightpipe-import.debug.log"
MAX_WAIT=30
WAIT_INTERVAL=2

# Continue to activate venv and run InsightPipe...

# --- Python Environment and Execution ---
#echo "$(date) — Activating virtual environment" >> "$LOGFILE"
#source /Users/crow/projects/insightpipe/.venv/bin/activate
#use uv to manage venv
echo "$(date) — Launching InsightPipe with config_import.yaml" >> "$LOGFILE"
cd /Users/crow/projects/insightpipe
/opt/homebrew/bin/uv run insightpipe.py \
  --config /Users/crow/projects/insightpipe/config_import.yaml \
  --watch

echo "$(date) — InsightPipe exited" >> "$LOGFILE"
