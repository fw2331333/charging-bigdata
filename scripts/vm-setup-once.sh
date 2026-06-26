#!/bin/bash
# =============================================================================
# 虚拟机一次性准备（按《新能源充电桩大数据项目.md》）
#   环境变量 / JDBC / HDFS 四文件 / MySQL 连通性
#
# 只需成功执行一次，以后日常只跑: bash scripts/run-pipeline.sh
#
# 用法（Ubuntu 虚拟机，项目共享目录）：
#   cd /media/sf_cs-/charging-bigdata
#   bash scripts/vm-setup-once.sh
# =============================================================================
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"

ENV_FILE="${ROOT}/config/pipeline.env"
EXAMPLE="${ROOT}/config/pipeline.env.example"
JAR_DIR="${ROOT}/spark/jars"
JDBC_VER="8.0.33"
JDBC_NAME="mysql-connector-j-${JDBC_VER}.jar"
JDBC_URL="https://repo1.maven.org/maven2/com/mysql/mysql-connector-j/${JDBC_VER}/${JDBC_NAME}"

log() { echo "[$(date '+%F %T')] $*"; }
die() { log "ERROR: $*"; exit 1; }

# --- 1. pipeline.env ---
if [[ ! -f "${ENV_FILE}" ]]; then
  cp "${EXAMPLE}" "${ENV_FILE}"
  log "已创建 ${ENV_FILE}，请填写 MYSQL_PASSWORD 后重新运行本脚本"
  exit 1
fi

# shellcheck source=lib/source-env.sh
source "${ROOT}/scripts/lib/source-env.sh" || die "加载 ${ENV_FILE} 失败"

export HADOOP_HOME="${HADOOP_HOME:-/usr/local/hadoop}"
export JAVA_HOME="${JAVA_HOME:-/usr/local/jdk1.8.0_162}"
export SPARK_HOME="${SPARK_HOME:-/usr/local/spark}"
export PATH="${JAVA_HOME}/bin:${SPARK_HOME}/bin:${HADOOP_HOME}/bin:${HADOOP_HOME}/sbin:${PATH}"
export HADOOP_CONF_DIR="${HADOOP_HOME}/etc/hadoop"

[[ -n "${MYSQL_PASSWORD:-}" && "${MYSQL_PASSWORD}" != "请修改" ]] \
  || die "请在 config/pipeline.env 中设置 MYSQL_PASSWORD"

log "========== 虚拟机一次性准备 START =========="
log "项目目录: ${ROOT}"

# --- 2. Hadoop / Spark ---
JPS_BIN="${JAVA_HOME}/bin/jps"
[[ -x "${JPS_BIN}" ]] || JPS_BIN="jps"
if ! "${JPS_BIN}" 2>/dev/null | grep -qE 'NameNode|namenode\.NameNode'; then
  if ! hdfs dfs -ls / >/dev/null 2>&1; then
    die "Hadoop 未启动。请先: start-dfs.sh && start-yarn.sh"
  fi
  log "WARN: jps 未列出 NameNode，但 HDFS 可访问"
else
  log "Hadoop 进程 OK"
fi

command -v spark-submit >/dev/null || die "未找到 spark-submit，检查 SPARK_HOME=${SPARK_HOME}"
log "Spark: $(spark-submit --version 2>&1 | head -1)"

# --- 3. MySQL JDBC（一次性下载）---
mkdir -p "${JAR_DIR}"
if [[ -n "${MYSQL_JDBC_JAR:-}" && -f "${MYSQL_JDBC_JAR}" ]]; then
  log "JDBC 已存在: ${MYSQL_JDBC_JAR}"
elif [[ -f "${JAR_DIR}/${JDBC_NAME}" ]]; then
  log "JDBC 已存在: ${JAR_DIR}/${JDBC_NAME}"
else
  log "下载 MySQL JDBC ..."
  if command -v wget >/dev/null; then
    wget -q -O "${JAR_DIR}/${JDBC_NAME}" "${JDBC_URL}"
  elif command -v curl >/dev/null; then
    curl -fsSL -o "${JAR_DIR}/${JDBC_NAME}" "${JDBC_URL}"
  else
    die "需要 wget 或 curl 下载 JDBC"
  fi
  log "JDBC 下载完成: ${JAR_DIR}/${JDBC_NAME}"
fi

# --- 4. MySQL 连通（Windows 宿主机）---
MYSQL_HOST="${MYSQL_HOST:-10.0.2.2}"
MYSQL_PORT="${MYSQL_PORT:-3306}"
MYSQL_USER="${MYSQL_USER:-root}"
MYSQL_DATABASE="${MYSQL_DATABASE:-charging_bigdata}"
log "测试 MySQL ${MYSQL_HOST}:${MYSQL_PORT}/${MYSQL_DATABASE} ..."
mysql -h "${MYSQL_HOST}" -P "${MYSQL_PORT}" -u"${MYSQL_USER}" -p"${MYSQL_PASSWORD}" \
  "${MYSQL_DATABASE}" -e "SELECT 1 AS ok;" >/dev/null \
  || die "无法连接 MySQL。请确认 Windows MySQL 已启动、allow_root_remote.sql 已执行、防火墙放行 3306"

# --- 5. HDFS 上传四个 CSV（指导书 5.1）---
need_upload=0
for f in dsv13r1.csv dsv13r2.csv nvv2t.csv nvv2t_md.csv; do
  hdfs dfs -test -e "/Car/${f}" || need_upload=1
done

if [[ "${need_upload}" == "1" ]]; then
  DATA_DIR=""
  for candidate in \
    "${DATASET_LOCAL_DIR:-}" \
    "/media/sf_cs-/dataset" \
    "/media/sf_cs-/项目2资料/数据集" \
    "${HOME}/dataset" \
    "${ROOT}/dataset"; do
    [[ -n "${candidate}" && -f "${candidate}/dsv13r1.csv" ]] && DATA_DIR="${candidate}" && break
  done
  [[ -n "${DATA_DIR}" ]] || die "未找到本地 CSV 目录。请将四个文件放到 ${DATASET_LOCAL_DIR:-/media/sf_cs-/dataset} 后重试"

  log "上传 HDFS /Car/ 来源: ${DATA_DIR}"
  bash "${ROOT}/hadoop/upload-data.sh" "${DATA_DIR}"
else
  log "HDFS /Car/ 四个 CSV 已存在，跳过上传"
fi

hdfs dfs -ls /Car | tee /dev/stderr | grep -q dsv13r1.csv || die "HDFS 缺少 dsv13r1.csv"
hdfs dfs -ls /Car | grep -q dsv13r2.csv || die "HDFS 缺少 dsv13r2.csv"

log "========== 一次性准备完成 =========="
log ""
log "以后日常只需一条命令（全量 MR + MySQL + Spark ADS）："
log "  cd ${ROOT} && bash scripts/run-pipeline.sh"
log ""
log "若 MR 已成功、只重跑 ADS："
log "  SKIP_MR=1 SKIP_ETL=0 bash scripts/run-pipeline.sh"
log ""
log "仅 Spark ADS："
log "  bash spark/scripts/run-spark-ads.sh"
