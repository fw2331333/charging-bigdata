#!/bin/bash
# 一键验证：HDFS + 编译 MR + 跑 v1 试任务
set -euo pipefail

source /etc/profile.d/hadoop.sh 2>/dev/null || true
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "==> 检查 Hadoop 进程"
jps | grep -E "NameNode|DataNode|ResourceManager|NodeManager" || {
  echo "[ERROR] Hadoop 未启动，请先: start-dfs.sh && start-yarn.sh"
  exit 1
}

echo "==> 检查 HDFS 数据"
hdfs dfs -test -e /Car/dsv13r1.csv || {
  echo "[ERROR] 未找到 /Car/dsv13r1.csv，请先 bash hadoop/upload-data.sh <数据目录>"
  exit 1
}

echo "==> 编译 MapReduce"
cd "${PROJECT_ROOT}/mapreduce"
mvn -q clean package

echo "==> 试跑 v1 任务"
hdfs dfs -rm -r -f /Car/output/v1-test 2>/dev/null || true
hadoop jar target/charging-mapreduce-1.0.0.jar \
  com.cbp.mr.v1.V1VoltageCurrentHourly \
  /Car/dsv13r1.csv /Car/output/v1-test

echo "==> 输出样例"
hdfs dfs -cat /Car/output/v1-test/part-r-00000 | head -5
echo ""
echo "[OK] 单机 Hadoop + MapReduce 验证通过。跑全部任务: bash mapreduce/run-all.sh"
