#!/bin/bash
# 导入 Web 演示用 MySQL（建表 + 预置数据，无需 Hadoop）
# 用法: bash scripts/import_web_demo.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MYSQL_HOST="${MYSQL_HOST:-127.0.0.1}"
MYSQL_PORT="${MYSQL_PORT:-3306}"
MYSQL_USER="${MYSQL_USER:-root}"
MYSQL_PASSWORD="${MYSQL_PASSWORD:-123456}"
MYSQL_DATABASE="${MYSQL_DATABASE:-charging_bigdata}"

mysql_exec() {
  mysql -h "${MYSQL_HOST}" -P "${MYSQL_PORT}" -u"${MYSQL_USER}" -p"${MYSQL_PASSWORD}" "$@"
}

echo "==> 重建数据库 ${MYSQL_DATABASE}"
mysql_exec -e "DROP DATABASE IF EXISTS ${MYSQL_DATABASE}; CREATE DATABASE ${MYSQL_DATABASE} DEFAULT CHARSET utf8mb4;"

for f in schema.sql ads_schema.sql seed/charging_bigdata_data.sql; do
  echo "==> sql/${f}"
  mysql_exec "${MYSQL_DATABASE}" < "${ROOT}/sql/${f}"
done

echo "[OK] 导入完成"
