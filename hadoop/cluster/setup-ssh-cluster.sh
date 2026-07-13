#!/bin/bash
# =============================================================================
# 三节点 SSH 免密互访（在 hadoop-master 上以 hadoop 用户执行）
#
# 前置：三台已安装 openssh-server，/etc/hosts 已按 cluster-hosts.example 配置
# 用法：bash hadoop/cluster/setup-ssh-cluster.sh
# =============================================================================
set -euo pipefail

NODES=(hadoop-master hadoop-slave1 hadoop-slave2)
HADOOP_USER="${HADOOP_USER:-hadoop}"

if [[ "$(whoami)" != "${HADOOP_USER}" ]]; then
  echo "[ERROR] 请以 ${HADOOP_USER} 用户运行（不要用 root）"
  exit 1
fi

echo "==> 生成本机 RSA 密钥（若不存在）"
mkdir -p ~/.ssh && chmod 700 ~/.ssh
[[ -f ~/.ssh/id_rsa ]] || ssh-keygen -t rsa -b 4096 -N "" -f ~/.ssh/id_rsa

echo "==> 收集 known_hosts"
for node in "${NODES[@]}"; do
  ssh-keyscan -H "${node}" >> ~/.ssh/known_hosts 2>/dev/null || true
done

echo "==> 将公钥分发到各节点（需输入各节点 hadoop 用户密码，仅首次）"
for node in "${NODES[@]}"; do
  echo "---- ${node} ----"
  ssh-copy-id -i ~/.ssh/id_rsa.pub "${HADOOP_USER}@${node}"
done

echo "==> 验证免密"
for node in "${NODES[@]}"; do
  ssh -o BatchMode=yes "${HADOOP_USER}@${node}" "hostname && whoami"
done

echo ""
echo "SSH 免密配置完成。Hadoop start-dfs.sh 将按 workers 文件 ssh 到各节点启动 DN/NM。"
