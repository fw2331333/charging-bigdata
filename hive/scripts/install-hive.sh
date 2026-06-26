#!/bin/bash
# =============================================================================
# [已弃用] 请改用 Spark SQL：spark/README.md
# 本脚本仅作历史参考，勿再执行。
# =============================================================================
set -euo pipefail

HIVE_VERSION="3.1.2"
HIVE_HOME="/usr/local/hive"
HADOOP_HOME="${HADOOP_HOME:-/usr/local/hadoop}"
JAVA_HOME="${JAVA_HOME:-/usr/local/jdk1.8.0_162}"
RUN_USER="${SUDO_USER:-fw}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

TGZ="apache-hive-${HIVE_VERSION}-bin.tar.gz"
# 官方包约 330MB+，小于 200MB 视为下载损坏
MIN_BYTES=200000000

MIRRORS=(
  "https://archive.apache.org/dist/hive/hive-${HIVE_VERSION}/${TGZ}"
  "https://downloads.apache.org/hive/hive-${HIVE_VERSION}/${TGZ}"
  "https://mirrors.tuna.tsinghua.edu.cn/apache/hive/hive-${HIVE_VERSION}/${TGZ}"
)

if [[ "${EUID}" -ne 0 ]]; then
  echo "[ERROR] 请使用: sudo bash hive/scripts/install-hive.sh"
  exit 1
fi

if [[ ! -d "${HADOOP_HOME}" ]]; then
  echo "[ERROR] 未找到 Hadoop: ${HADOOP_HOME}"
  exit 1
fi

log() { echo "==> $*"; }

verify_tgz() {
  local file="$1"
  [[ -f "${file}" ]] || return 1
  local size
  size="$(stat -c%s "${file}" 2>/dev/null || echo 0)"
  [[ "${size}" -ge "${MIN_BYTES}" ]] || return 1
  tar -tzf "${file}" >/dev/null 2>&1
}

download_hive() {
  local dest="/tmp/${TGZ}"
  rm -f "${dest}"

  # 优先：项目内 packages/ 或共享目录已放好完整包
  for local_pkg in \
    "${PROJECT_ROOT}/hive/packages/${TGZ}" \
    "/media/sf_cs-/charging-bigdata/hive/packages/${TGZ}"; do
    if verify_tgz "${local_pkg}"; then
      log "使用本地安装包: ${local_pkg}"
      cp -f "${local_pkg}" "${dest}"
      return 0
    fi
  done

  log "从镜像下载 Hive ${HIVE_VERSION}（约 330MB，请耐心等待）"
  for url in "${MIRRORS[@]}"; do
    log "尝试: ${url}"
    if wget -c --timeout=60 --tries=3 -O "${dest}.part" "${url}"; then
      mv -f "${dest}.part" "${dest}"
      if verify_tgz "${dest}"; then
        log "下载成功: ${dest}"
        return 0
      fi
      log "WARN: 文件损坏，尝试下一个镜像"
      rm -f "${dest}"
    fi
  done
  echo "[ERROR] 下载失败。请 Windows 浏览器下载 ${TGZ} 放到:"
  echo "  ${PROJECT_ROOT}/hive/packages/${TGZ}"
  echo "然后重新运行本脚本。"
  exit 1
}

log "安装依赖"
apt-get update -qq
DEBIAN_FRONTEND=noninteractive apt-get install -y wget tar

if [[ ! -d "${HIVE_HOME}" ]]; then
  download_hive
  cd /tmp
  rm -rf "/tmp/apache-hive-${HIVE_VERSION}-bin"
  log "解压 ${TGZ}"
  tar -xzf "/tmp/${TGZ}"
  mv "/tmp/apache-hive-${HIVE_VERSION}-bin" "${HIVE_HOME}"
else
  log "Hive 目录已存在，跳过下载: ${HIVE_HOME}"
fi

chown -R "${RUN_USER}:${RUN_USER}" "${HIVE_HOME}"

log "配置 hive-env.sh"
cat > "${HIVE_HOME}/conf/hive-env.sh" <<EOF
export HADOOP_HOME=${HADOOP_HOME}
export HIVE_CONF_DIR=${HIVE_HOME}/conf
export JAVA_HOME=${JAVA_HOME}
EOF

log "配置 hive-site.xml（Derby 内嵌元数据库）"
cat > "${HIVE_HOME}/conf/hive-site.xml" <<'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
  <property>
    <name>javax.jdo.option.ConnectionURL</name>
    <value>jdbc:derby:;databaseName=/usr/local/hive/metastore_db;create=true</value>
  </property>
  <property>
    <name>javax.jdo.option.ConnectionDriverName</name>
    <value>org.apache.derby.jdbc.EmbeddedDriver</value>
  </property>
  <property>
    <name>hive.metastore.warehouse.dir</name>
    <value>/warehouse/hive</value>
  </property>
  <property>
    <name>hive.metastore.schema.verification</name>
    <value>false</value>
  </property>
  <property>
    <name>datanucleus.schema.autoCreateAll</name>
    <value>true</value>
  </property>
  <property>
    <name>hive.cli.print.header</name>
    <value>true</value>
  </property>
</configuration>
EOF

log "环境变量 /etc/profile.d/hive.sh"
cat > /etc/profile.d/hive.sh <<EOF
export JAVA_HOME=${JAVA_HOME}
export HADOOP_HOME=${HADOOP_HOME}
export HIVE_HOME=${HIVE_HOME}
export HIVE_CONF_DIR=\${HIVE_HOME}/conf
export PATH=\$PATH:\${HIVE_HOME}/bin
EOF
chmod +x /etc/profile.d/hive.sh

log "创建 HDFS 目录"
sudo -u "${RUN_USER}" bash -lc "
  export JAVA_HOME=${JAVA_HOME}
  export HADOOP_HOME=${HADOOP_HOME}
  export PATH=\$JAVA_HOME/bin:\$HADOOP_HOME/bin:\$HADOOP_HOME/sbin:\$PATH
  hdfs dfs -mkdir -p /warehouse/hive /warehouse/ods /tmp/hive
  hdfs dfs -chmod -R 775 /warehouse /tmp/hive || true
"

echo ""
echo "=============================================="
echo " Hive 已安装: ${HIVE_HOME}"
echo ""
echo " 下一步（用户 ${RUN_USER}）："
echo "   source /etc/profile.d/hive.sh"
echo "   schematool -dbType derby -initSchema    # 仅首次"
echo "   hive --version"
echo "   bash hive/scripts/prepare_ods_paths.sh"
echo "   hive -f hive/ddl/01_ods_external.sql"
echo "=============================================="
