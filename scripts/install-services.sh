#!/bin/bash

# Installation script for InsightPipe systemd services
# Run this script with sudo

set -e

APP_DIR="/opt/dockerapps/insightpipe"
SCRIPTS_DIR="$APP_DIR/scripts"

echo "Installing InsightPipe systemd services..."

# Create log directory
echo "Creating log directory..."
mkdir -p /var/log/insightpipe
chown proxdoc:proxdoc /var/log/insightpipe

# Make startup scripts executable
echo "Making startup scripts executable..."
chmod +x "$SCRIPTS_DIR/start-app.sh"
chmod +x "$SCRIPTS_DIR/start-insightpipe-detection.sh"
chmod +x "$SCRIPTS_DIR/start-insightpipe-import.sh"

# Copy service files to systemd directory
echo "Copying service files to /etc/systemd/system/..."
cp "$SCRIPTS_DIR/insightpipe-app.service" /etc/systemd/system/
cp "$SCRIPTS_DIR/insightpipe-detection.service" /etc/systemd/system/
cp "$SCRIPTS_DIR/insightpipe-import.service" /etc/systemd/system/

# Reload systemd daemon
echo "Reloading systemd daemon..."
systemctl daemon-reload

echo ""
echo "Installation complete!"
echo ""
echo "Available commands:"
echo "  Start services:"
echo "    sudo systemctl start insightpipe-app"
echo "    sudo systemctl start insightpipe-detection"
echo "    sudo systemctl start insightpipe-import"
echo ""
echo "  Enable services to start on boot:"
echo "    sudo systemctl enable insightpipe-app"
echo "    sudo systemctl enable insightpipe-detection"
echo "    sudo systemctl enable insightpipe-import"
echo ""
echo "  Check status:"
echo "    sudo systemctl status insightpipe-app"
echo "    sudo systemctl status insightpipe-detection"
echo "    sudo systemctl status insightpipe-import"
echo ""
echo "  View logs:"
echo "    sudo journalctl -u insightpipe-app -f"
echo "    sudo journalctl -u insightpipe-detection -f"
echo "    sudo journalctl -u insightpipe-import -f"
echo ""
echo "  Or check log files:"
echo "    tail -f /var/log/insightpipe/app.log"
echo "    tail -f /var/log/insightpipe/detection.log"
echo "    tail -f /var/log/insightpipe/import.log"
