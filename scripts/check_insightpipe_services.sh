#!/bin/bash

# Check status of InsightPipe systemd services on Debian/Linux

echo "🛠️ Checking InsightPipe Services..."
echo ""

SERVICES=(
    "insightpipe-app"
    "insightpipe-detection"
    "insightpipe-import"
)

for service in "${SERVICES[@]}"; do
    echo "🔹 $service.service"
    
    # Check if service exists
    if ! systemctl list-unit-files | grep -q "^${service}.service"; then
        echo "    ❌ Service not installed"
        echo ""
        continue
    fi
    
    # Get service status
    if systemctl is-active --quiet "$service"; then
        pid=$(systemctl show -p MainPID --value "$service")
        echo "    ✅ Running (PID: $pid)"
    else
        echo "    ⚠️ Not running"
    fi
    
    # Check if enabled
    if systemctl is-enabled --quiet "$service" 2>/dev/null; then
        echo "    🔄 Enabled (starts on boot)"
    else
        echo "    ⏸️ Disabled (won't start on boot)"
    fi
    
    # Get last exit status and recent log entries
    failed_status=$(systemctl show -p Result --value "$service")
    if [[ "$failed_status" != "success" ]]; then
        echo "    ⚠️ Last result: $failed_status"
    fi
    
    # Show last few log lines
    echo "    📋 Recent logs:"
    journalctl -u "$service" -n 3 --no-pager --output=cat 2>/dev/null | sed 's/^/       /'
    
    echo ""
done

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "💡 Useful commands:"
echo "   View live logs:    sudo journalctl -u insightpipe-app -f"
echo "   Restart service:   sudo systemctl restart insightpipe-app"
echo "   Enable on boot:    sudo systemctl enable insightpipe-app"
echo "   Full status:       sudo systemctl status insightpipe-app"
