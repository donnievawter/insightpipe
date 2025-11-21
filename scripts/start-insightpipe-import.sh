#!/bin/bash

# InsightPipe Import Service Startup Script
# This script runs the import pipeline with config_import.yaml

LOGFILE="/var/log/insightpipe/import.log"
APP_DIR="/opt/dockerapps/insightpipe"

# Ensure log directory exists
mkdir -p /var/log/insightpipe

echo "$(date) — Starting InsightPipe Import Service" >> "$LOGFILE"
cd "$APP_DIR"

# Add any environment variables here if needed
# export VARIABLE_NAME=value

echo "$(date) — Working directory: $(pwd)" >> "$LOGFILE"

# Set log file for insightpipe.py
export INSIGHTPIPE_LOGFILE="$LOGFILE"

# Add any environment variables here if needed
# export VARIABLE_NAME=value
echo "$(date) — Running: uv run insightpipe.py --config config_import.yaml --watch" >> "$LOGFILE"

# Run the import pipeline
/home/proxdoc/.local/bin/uv run insightpipe.py \
  --config "$APP_DIR/config_import.yaml" \
  --watch 2>&1 | tee -a "$LOGFILE"

echo "$(date) — InsightPipe Import Service exited" >> "$LOGFILE"
