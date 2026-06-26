#!/bin/bash
# 在 Hadoop 节点执行全部 MapReduce 任务（v1~v7）
# Jar 默认 Main-Class 为 JobRunner，只需传：输入路径、输出根目录
set -euo pipefail

INPUT="${1:-/Car/dsv13r1.csv}"
OUTPUT_BASE="${2:-/Car/output}"
JAR="${3:-target/charging-mapreduce-1.0.0.jar}"

if [ ! -f "$JAR" ]; then
  echo "[ERROR] Jar not found: $JAR"
  echo "Run: mvn clean package"
  exit 1
fi

echo "Input      : $INPUT"
echo "Output base: $OUTPUT_BASE"
echo "Jar        : $JAR"

hadoop jar "${JAR}" "${INPUT}" "${OUTPUT_BASE}"

echo ""
echo "[DONE] All 7 MapReduce jobs finished. Sample v1:"
hdfs dfs -cat "${OUTPUT_BASE}/v1/part-r-00000" 2>/dev/null | head -3 || true
