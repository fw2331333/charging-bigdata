#!/usr/bin/env bash
# 一键修复 Datart：数据源 + 视图 + 七图图表 + Dashboard 排版（RC.3 完整 styles）
# 默认 admin/123456  mysql/Charging@2026
set -euo pipefail
export DATART_URL="${DATART_URL:-http://127.0.0.1:8088}"
export DATART_USER="${DATART_USER:-admin}"
export DATART_PASSWORD="${DATART_PASSWORD:-123456}"
export MYSQL_HOST="${MYSQL_HOST:-mysql}"
export MYSQL_PASSWORD="${MYSQL_PASSWORD:-Charging@2026}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
exec python3 "$ROOT/scripts/fix_datart_all.py"
