#!/usr/bin/env bash
# flight_monitor.sh - crontab wrapper with timestamped logging
# Usage:
#   Direct:  ./flight_monitor.sh
#   Crontab: 0 9,21 * * * /path/to/flight_monitor.sh >> /var/log/flight-monitor.log 2>&1

set -euo pipefail

readonly SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
readonly PYTHON="${PYTHON:-python3}"
readonly CONFIG="${FLIGHT_MONITOR_CONFIG:-$SCRIPT_DIR/config.yaml}"
readonly TIMESTAMP="$(date '+%Y-%m-%d %H:%M:%S')"

echo "[$TIMESTAMP] Flight monitor started"

if [ ! -f "$CONFIG" ]; then
  echo "[$TIMESTAMP] ERROR: config file not found: $CONFIG" >&2
  exit 1
fi

"$PYTHON" "$SCRIPT_DIR/flight_check_cron.py" --config "$CONFIG" 2>&1

readonly EXIT_CODE=$?
readonly END_TS="$(date '+%Y-%m-%d %H:%M:%S')"

if [ $EXIT_CODE -eq 0 ]; then
  echo "[$END_TS] Done (exit 0)"
else
  echo "[$END_TS] Done with errors (exit $EXIT_CODE)" >&2
fi

exit $EXIT_CODE