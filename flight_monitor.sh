#!/usr/bin/env bash
# flight_monitor.sh - Linux crontab 封装
# 用法: crontab -e 添加:
#   0 3,9,15,21 * * * /path/to/flight_monitor.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON="${PYTHON:-python3}"

# 执行监控脚本
"$PYTHON" "$SCRIPT_DIR/flight_check_cron.py" --config "$SCRIPT_DIR/config.yaml" 2>&1
