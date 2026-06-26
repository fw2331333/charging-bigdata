#!/bin/bash
# 流水线跑完后的快速验收（MySQL 行数 + HDFS 输出）
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${ROOT}/config/pipeline.env"
# shellcheck source=lib/source-env.sh
source "${ROOT}/scripts/lib/source-env.sh"

export HADOOP_HOME="${HADOOP_HOME:-/usr/local/hadoop}"
export PATH="${HADOOP_HOME}/bin:${PATH}"

echo "==> HDFS MR 输出"
for v in v1 v2 v3 v4 v5 v6 v7; do
  hdfs dfs -test -e "${HDFS_OUTPUT_BASE:-/Car/output}/${v}/part-r-00000" \
    && echo "  OK ${v}" || echo "  MISSING ${v}"
done

echo ""
echo "==> MySQL 表行数"
mysql -h "${MYSQL_HOST}" -P "${MYSQL_PORT}" -u"${MYSQL_USER}" -p"${MYSQL_PASSWORD}" \
  "${MYSQL_DATABASE}" -N -e "
SELECT 'MR t_voltage_current', COUNT(*) FROM t_voltage_current
UNION ALL SELECT 'ADS t_soc_hourly', COUNT(*) FROM t_soc_hourly
UNION ALL SELECT 'ADS t_charging_daily', COUNT(*) FROM t_charging_daily
UNION ALL SELECT 'ADS t_soc_heatmap', COUNT(*) FROM t_soc_heatmap
UNION ALL SELECT 'ADS t_charge_rate_hourly', COUNT(*) FROM t_charge_rate_hourly;
"

echo ""
echo "==> ADS 充电日期样例（nvv2t 会话，created 规范化后）"
mysql -h "${MYSQL_HOST}" -P "${MYSQL_PORT}" -u"${MYSQL_USER}" -p"${MYSQL_PASSWORD}" \
  "${MYSQL_DATABASE}" -e "SELECT * FROM t_charging_daily ORDER BY record_date LIMIT 5;"
