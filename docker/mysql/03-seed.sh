#!/bin/bash
# MySQL 容器首次启动时导入种子数据（需已执行 schema + ads_schema）
set -e
mysql -uroot -p"${MYSQL_ROOT_PASSWORD}" charging_bigdata < /seed-data.sql
