#!/bin/bash

# InsightPipe Web Application Startup Script
# This script runs the Flask web application

LOGFILE="/var/log/insightpipe/app.log"
APP_DIR="/opt/dockerapps/insightpipe"

# Ensure log directory exists
mkdir -p /var/log/insightpipe

echo "$(date) — Starting InsightPipe Web Application" >> "$LOGFILE"
cd "$APP_DIR"

# Add any environment variables here if needed
# export VARIABLE_NAME=value

echo "$(date) — Working directory: $(pwd)" >> "$LOGFILE"
echo "$(date) — Running: uv run app.py" >> "$LOGFILE"

# Run the Flask app
/home/proxdoc/.local/bin/uv run app.py 2>&1 | tee -a "$LOGFILE"

echo "$(date) — InsightPipe Web Application exited" >> "$LOGFILE"
