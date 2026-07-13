#!/usr/bin/env bash
# 旧库升级 v6/v7 表结构（幂等）。在 MySQL 容器可达时执行。
# 用法：bash scripts/apply_v6_v7_migration.sh [mysql_root_password]
set -euo pipefail

MYSQL_PW="${1:-charging123}"
DB=charging_bigdata

mysql_exec() {
  docker exec cbp-mysql mysql -uroot -p"$MYSQL_PW" "$DB" -e "$1"
}

has_column() {
  docker exec cbp-mysql mysql -uroot -p"$MYSQL_PW" -N -e \
    "SELECT COUNT(*) FROM information_schema.COLUMNS
     WHERE TABLE_SCHEMA='$DB' AND TABLE_NAME='$1' AND COLUMN_NAME='$2';"
}

echo "[migrate] t_voltage_current_relation ..."
if [[ "$(has_column t_voltage_current_relation voltage_change_rate)" == "0" ]]; then
  if [[ "$(has_column t_voltage_current_relation record_time)" == "1" ]]; then
    mysql_exec "ALTER TABLE t_voltage_current_relation DROP INDEX uk_record_time;" 2>/dev/null || true
    mysql_exec "ALTER TABLE t_voltage_current_relation
      CHANGE COLUMN record_time record_hour VARCHAR(20) NOT NULL COMMENT 'hour HH',
      CHANGE COLUMN pack_voltage voltage_change_rate DOUBLE COMMENT 'voltage change pct',
      CHANGE COLUMN charge_current current_change_rate DOUBLE COMMENT 'current change pct';"
    mysql_exec "ALTER TABLE t_voltage_current_relation ADD UNIQUE KEY uk_record_hour (record_hour);" 2>/dev/null || true
    echo "      -> migrated v6 columns"
  else
    echo "      !! v6 表结构未知，请 DESCRIBE t_voltage_current_relation 后手动处理"
    exit 1
  fi
else
  echo "      -> v6 schema already new"
fi

echo "[migrate] t_soc_temperature ..."
if [[ "$(has_column t_soc_temperature battery_status)" == "0" ]]; then
  if [[ "$(has_column t_soc_temperature soc_bucket)" == "1" ]]; then
    mysql_exec "ALTER TABLE t_soc_temperature DROP INDEX uk_soc_bucket;" 2>/dev/null || true
    mysql_exec "ALTER TABLE t_soc_temperature
      CHANGE COLUMN soc_bucket battery_status VARCHAR(20) NOT NULL COMMENT 'idle/charging/discharging';"
    if [[ "$(has_column t_soc_temperature var_max_temperature)" == "0" ]]; then
      mysql_exec "ALTER TABLE t_soc_temperature
        ADD COLUMN var_max_temperature DOUBLE COMMENT 'var max temp' AFTER avg_min_temperature,
        ADD COLUMN var_min_temperature DOUBLE COMMENT 'var min temp' AFTER var_max_temperature;"
    fi
    mysql_exec "ALTER TABLE t_soc_temperature ADD UNIQUE KEY uk_battery_status (battery_status);" 2>/dev/null || true
    echo "      -> migrated v7 columns"
  else
    echo "      !! v7 表结构未知，请 DESCRIBE t_soc_temperature 后手动处理"
    exit 1
  fi
else
  if [[ "$(has_column t_soc_temperature var_max_temperature)" == "0" ]]; then
    mysql_exec "ALTER TABLE t_soc_temperature
      ADD COLUMN var_max_temperature DOUBLE COMMENT 'var max temp' AFTER avg_min_temperature,
      ADD COLUMN var_min_temperature DOUBLE COMMENT 'var min temp' AFTER var_max_temperature;"
    echo "      -> added v7 variance columns"
  else
    echo "      -> v7 schema already new"
  fi
fi

mysql_exec "CREATE OR REPLACE VIEW v_soc_temperature AS
  SELECT battery_status, avg_max_temperature, avg_min_temperature,
         var_max_temperature, var_min_temperature
  FROM t_soc_temperature;" 2>/dev/null || true

echo "[migrate] done"
