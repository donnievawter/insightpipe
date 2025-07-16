#!/bin/bash

echo "🛠️ Checking InsightPipe LaunchAgents..."

launchctl list | grep insightpipe | while read -r pid status label; do
  echo "🔹 $label"
  if [[ "$pid" == "-" ]]; then
    echo "    ➤ Not running (loaded but inactive)"
  else
    echo "    ➤ PID: $pid | Exit Status: $status"
  fi

  # Suggest potential error interpretation
  case "$status" in
    0) echo "    ✅ Last run exited cleanly" ;;
    78) echo "    ⚠️ Function not implemented (possible exec or script issue)" ;;
    *) echo "    ⚠️ Exit code $status — investigate logs or script output" ;;
  esac
done

