#!/bin/bash
# =============================================================================
# Ubuntu 单机伪分布式 Hadoop 3.1.3 安装脚本
# 用法：sudo bash install-pseudo-distributed.sh
# 说明：先单机跑通 MR；扩展真三节点见 docs/三节点集群部署手册.md
# =============================================================================
set -euo pipefail

HADOOP_VERSION="3.1.3"
HADOOP_USER="${HADOOP_USER:-hadoop}"
HADOOP_HOME="/opt/hadoop-${HADOOP_VERSION}"
INSTALL_DIR="/opt"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ "${EUID}" -ne 0 ]]; then
  echo "[ERROR] 请使用 sudo 运行"
  exit 1
fi

echo "==> 安装依赖（JDK8、SSH、rsync）"
apt-get update -qq
DEBIAN_FRONTEND=noninteractive apt-get install -y openjdk-8-jdk openssh-server rsync wget curl

echo "==> 创建 hadoop 用户"
if ! id "${HADOOP_USER}" &>/dev/null; then
  useradd -m -s /bin/bash "${HADOOP_USER}"
fi

echo "==> 配置本机主机名 hadoop-master（/etc/hosts）"
grep -q "hadoop-master" /etc/hosts || echo "127.0.0.1 hadoop-master" >> /etc/hosts
hostnamectl set-hostname hadoop-master 2>/dev/null || hostname hadoop-master

echo "==> 下载 Hadoop ${HADOOP_VERSION}"
if [[ ! -d "${HADOOP_HOME}" ]]; then
  cd /tmp
  wget -q "https://archive.apache.org/dist/hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz"
  tar -xzf "hadoop-${HADOOP_VERSION}.tar.gz" -C "${INSTALL_DIR}"
  chown -R "${HADOOP_USER}:${HADOOP_USER}" "${HADOOP_HOME}"
fi

echo "==> 写入配置文件（伪分布式）"
cp -f "${SCRIPT_DIR}/conf-pseudo/"*.xml "${HADOOP_HOME}/etc/hadoop/"
cp -f "${SCRIPT_DIR}/conf-pseudo/workers" "${HADOOP_HOME}/etc/hadoop/workers"

echo "==> 创建数据目录"
mkdir -p /data/hadoop/{tmp,hdfs/namenode,hdfs/datanode}
chown -R "${HADOOP_USER}:${HADOOP_USER}" /data/hadoop

echo "==> 配置 hadoop 用户环境变量"
cat > /etc/profile.d/hadoop.sh <<EOF
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
export HADOOP_HOME=${HADOOP_HOME}
export HADOOP_CONF_DIR=\${HADOOP_HOME}/etc/hadoop
export PATH=\$PATH:\$HADOOP_HOME/bin:\$HADOOP_HOME/sbin
EOF
chmod +x /etc/profile.d/hadoop.sh

echo "==> 配置 SSH 免密（本机）"
sudo -u "${HADOOP_USER}" bash -c '
  mkdir -p ~/.ssh && chmod 700 ~/.ssh
  [[ -f ~/.ssh/id_rsa ]] || ssh-keygen -t rsa -N "" -f ~/.ssh/id_rsa
  cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
  chmod 600 ~/.ssh/authorized_keys
  ssh-keyscan -H hadoop-master localhost 127.0.0.1 >> ~/.ssh/known_hosts 2>/dev/null || true
'

echo "==> 首次格式化 NameNode（仅第一次安装执行）"
if [[ ! -d /data/hadoop/hdfs/namenode/current ]]; then
  sudo -u "${HADOOP_USER}" bash -lc "source /etc/profile.d/hadoop.sh && hdfs namenode -format -force"
else
  echo "    NameNode 已格式化，跳过"
fi

echo ""
echo "=============================================="
echo " 安装完成。以 hadoop 用户启动："
echo "   sudo su - hadoop"
echo "   source /etc/profile.d/hadoop.sh"
echo "   start-dfs.sh && start-yarn.sh"
echo "   jps   # 应看到 NameNode DataNode ResourceManager NodeManager"
echo " Web UI: http://hadoop-master:9870  YARN: http://hadoop-master:8088"
echo "=============================================="
