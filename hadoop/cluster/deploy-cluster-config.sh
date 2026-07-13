#!/bin/bash
# =============================================================================
# 将 conf-cluster 全套配置同步到三节点（在 hadoop-master 上以 hadoop 用户执行）
#
# 企业实践：配置与代码分离；计算层只读 HDFS，结果经独立 ETL 写入 MySQL 服务层
#
# 用法：
#   export HADOOP_HOME=/opt/hadoop-3.1.3   # 与 install-pseudo-distributed.sh 一致
#   bash hadoop/cluster/deploy-cluster-config.sh
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_HADOOP="$(cd "${SCRIPT_DIR}/.." && pwd)"
CONF_SRC="${REPO_HADOOP}/conf-cluster"
NODES=(hadoop-master hadoop-slave1 hadoop-slave2)

HADOOP_HOME="${HADOOP_HOME:-/opt/hadoop-3.1.3}"
HADOOP_USER="${HADOOP_USER:-hadoop}"
REMOTE_CONF="${HADOOP_HOME}/etc/hadoop"

if [[ "$(whoami)" != "${HADOOP_USER}" ]]; then
  echo "[ERROR] 请以 ${HADOOP_USER} 用户运行"
  exit 1
fi

for f in core-site.xml hdfs-site.xml yarn-site.xml mapred-site.xml workers hadoop-env.sh; do
  [[ -f "${CONF_SRC}/${f}" ]] || { echo "缺少 ${CONF_SRC}/${f}"; exit 1; }
done

echo "==> 本机写入集群配置 -> ${REMOTE_CONF}"
mkdir -p "${REMOTE_CONF}"
cp -f "${CONF_SRC}/"*.xml "${REMOTE_CONF}/"
cp -f "${CONF_SRC}/workers" "${REMOTE_CONF}/workers"
# hadoop-env.sh：追加 JVM 参数（保留原文件其他内容）
if grep -q "HDFS_NAMENODE_OPTS" "${REMOTE_CONF}/hadoop-env.sh" 2>/dev/null; then
  echo "    hadoop-env.sh 已含 JVM 配置，跳过覆盖"
else
  cat "${CONF_SRC}/hadoop-env.sh" >> "${REMOTE_CONF}/hadoop-env.sh"
fi

echo "==> 创建数据目录（三台路径必须一致）"
for node in "${NODES[@]}"; do
  echo "---- ${node} ----"
  ssh "${node}" "sudo mkdir -p /data/hadoop/{tmp,hdfs/namenode,hdfs/datanode} && sudo chown -R ${HADOOP_USER}:${HADOOP_USER} /data/hadoop"
done

echo "==> rsync 配置到 Slave 节点"
for node in hadoop-slave1 hadoop-slave2; do
  echo "---- ${node} ----"
  ssh "${node}" "mkdir -p ${REMOTE_CONF}"
  rsync -avz "${REMOTE_CONF}/" "${node}:${REMOTE_CONF}/"
done

echo ""
echo "配置已同步。若从单机扩为三节点且已有数据，请勿重新 format。"
echo "在 Master 执行：start-dfs.sh && start-yarn.sh"
echo "验证：bash hadoop/cluster/verify-cluster.sh"
