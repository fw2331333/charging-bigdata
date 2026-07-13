#!/bin/bash
# =============================================================================
# 三节点集群健康检查（在 hadoop-master 上执行，需已 start-dfs.sh && start-yarn.sh）
# 用法：bash hadoop/cluster/verify-cluster.sh
# =============================================================================
set -euo pipefail

HADOOP_HOME="${HADOOP_HOME:-/opt/hadoop-3.1.3}"
export HADOOP_HOME
export PATH="${HADOOP_HOME}/bin:${HADOOP_HOME}/sbin:${PATH}"

EXPECTED_DN=3
EXPECTED_NM=3

echo "==> HDFS DataNode 报告"
hdfs dfsadmin -report | tee /tmp/cbp_dfs_report.txt
LIVE_DN=$(grep -c "Live datanodes" /tmp/cbp_dfs_report.txt || true)
DN_COUNT=$(awk '/Live datanodes \(/{getline; print $1}' /tmp/cbp_dfs_report.txt | head -1)
DN_COUNT="${DN_COUNT:-0}"

echo ""
echo "==> YARN NodeManager 列表"
yarn node -list 2>/dev/null | tee /tmp/cbp_yarn_nodes.txt || true
NM_COUNT=$(grep -c "RUNNING" /tmp/cbp_yarn_nodes.txt || echo 0)

echo ""
echo "==> 副本策略"
hdfs dfs -stat '%r' / 2>/dev/null || true

echo ""
echo "==> 汇总"
echo "  Live DataNodes : ${DN_COUNT} (期望 >= ${EXPECTED_DN})"
echo "  RUNNING NM     : ${NM_COUNT} (期望 >= ${EXPECTED_NM})"

FAIL=0
if [[ "${DN_COUNT}" -lt "${EXPECTED_DN}" ]]; then
  echo "[FAIL] DataNode 数量不足，检查 workers、SSH 免密、Slave 上 HADOOP_HOME"
  FAIL=1
fi
if [[ "${NM_COUNT}" -lt "${EXPECTED_NM}" ]]; then
  echo "[FAIL] NodeManager 数量不足"
  FAIL=1
fi

if [[ "${FAIL}" -eq 0 ]]; then
  echo "[OK] 三节点集群就绪，可执行 bash scripts/run-pipeline.sh"
  exit 0
fi
exit 1
