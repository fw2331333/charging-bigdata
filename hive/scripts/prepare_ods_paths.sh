#!/bin/bash
# 将 /Car/*.csv 复制到 Hive 外部表目录（每表一目录）
set -euo pipefail

HADOOP_HOME="${HADOOP_HOME:-/usr/local/hadoop}"
export PATH="${HADOOP_HOME}/bin:${PATH}"

hdfs dfs -mkdir -p /warehouse/ods/dsv13r1 /warehouse/ods/dsv13r2 /warehouse/ods/nvv2t

for pair in "dsv13r1:dsv13r1.csv" "dsv13r2:dsv13r2.csv" "nvv2t:nvv2t.csv"; do
  dir="${pair%%:*}"
  file="${pair##*:}"
  src="/Car/${file}"
  dst="/warehouse/ods/${dir}/"
  hdfs dfs -test -e "${src}" || { echo "缺少 ${src}"; exit 1; }
  hdfs dfs -rm -f "${dst}"* 2>/dev/null || true
  hdfs dfs -cp -f "${src}" "${dst}data.csv"
  echo "OK ${src} -> ${dst}"
done

echo "完成。可执行: hive -f hive/ddl/01_ods_external.sql"
