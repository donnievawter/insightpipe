#!/bin/bash

# InsightPipe Detection Service Startup Script
# This script runs the detection pipeline with config_detection.yaml

LOGFILE="/var/log/insightpipe/detection.log"
APP_DIR="/opt/dockerapps/insightpipe"

# Ensure log directory exists
mkdir -p /var/log/insightpipe

echo "$(date) — Starting InsightPipe Detection Service" >> "$LOGFILE"
cd "$APP_DIR"

# Add any environment variables here if needed
# export VARIABLE_NAME=value

echo "$(date) — Working directory: $(pwd)" >> "$LOGFILE"

# Set log file for insightpipe.py
export INSIGHTPIPE_LOGFILE="$LOGFILE"

# Add any environment variables here if needed
# export VARIABLE_NAME=value
echo "$(date) — Running: uv run insightpipe.py --config config_detection.yaml --watch" >> "$LOGFILE"

# Run the detection pipeline
/home/proxdoc/.local/bin/uv run insightpipe.py \
  --config "$APP_DIR/config_detection.yaml" \
  --watch 2>&1 | tee -a "$LOGFILE"

echo "$(date) — InsightPipe Detection Service exited" >> "$LOGFILE"
