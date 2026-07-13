#!/bin/bash
# =============================================================================
# 企业式离线批处理流水线（单入口）
#
# 阶段：
#   1. Preflight   — Hadoop / HDFS / MySQL
#   2. MapReduce   — v1~v7 写 HDFS（计算层，不连 MySQL）
#   3. ETL         — analytics/etl 幂等写入 MySQL 服务层
#   4. Spark ADS   — dsv13r2 + nvv2t 汇总入 MySQL
#
# 首次：bash scripts/vm-setup-once.sh
# 三节点：docs/三节点集群部署手册.md
# 架构：docs/企业级架构与ETL设计.md
# =============================================================================
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"

ENV_FILE="${ROOT}/config/pipeline.env"
LOG_DIR="${ROOT}/logs"
mkdir -p "${LOG_DIR}"
LOG_FILE="${LOG_DIR}/pipeline-$(date +%Y%m%d-%H%M%S).log"

log() { echo "[$(date '+%F %T')] $*" | tee -a "${LOG_FILE}"; }
die() { log "ERROR: $*"; exit 1; }

if [[ ! -f "${ENV_FILE}" ]]; then
  die "缺少 ${ENV_FILE}，请复制 pipeline.env.example 并填写 MySQL 等配置"
fi
# shellcheck source=lib/source-env.sh
source "${ROOT}/scripts/lib/source-env.sh" || die "加载 ${ENV_FILE} 失败"

export HADOOP_HOME="${HADOOP_HOME:-/opt/hadoop-3.1.3}"
export JAVA_HOME="${JAVA_HOME:-/usr/lib/jvm/java-8-openjdk-amd64}"
export SPARK_HOME="${SPARK_HOME:-/usr/local/spark}"
export PATH="${JAVA_HOME}/bin:${SPARK_HOME}/bin:${HADOOP_HOME}/bin:${HADOOP_HOME}/sbin:${PATH}"
export HADOOP_CONF_DIR="${HADOOP_HOME}/etc/hadoop"

HDFS_INPUT="${HDFS_INPUT:-/Car/dsv13r1.csv}"
HDFS_OUTPUT_BASE="${HDFS_OUTPUT_BASE:-/Car/output}"
MYSQL_HOST="${MYSQL_HOST:-10.0.2.2}"
MYSQL_PORT="${MYSQL_PORT:-3306}"
MYSQL_USER="${MYSQL_USER:-root}"
MYSQL_PASSWORD="${MYSQL_PASSWORD:-}"
MYSQL_DATABASE="${MYSQL_DATABASE:-charging_bigdata}"

export MYSQL_HOST MYSQL_PORT MYSQL_USER MYSQL_PASSWORD MYSQL_DATABASE

log "========== 充电桩大数据离线流水线 START =========="
log "项目目录: ${ROOT}"
log "日志文件: ${LOG_FILE}"

# --- 预检 ---
log "预检: Hadoop 进程"
JPS_BIN="${JAVA_HOME}/bin/jps"
[[ -x "${JPS_BIN}" ]] || JPS_BIN="jps"
if ! "${JPS_BIN}" 2>/dev/null | tee -a "${LOG_FILE}" | grep -qE 'NameNode|namenode\.NameNode'; then
  if ! hdfs dfs -ls / >/dev/null 2>&1; then
    die "NameNode 未启动，请先 start-dfs.sh && start-yarn.sh"
  fi
  log "WARN: jps 未列出 NameNode（可能 JDK 路径不一致），但 HDFS 可访问，继续"
fi

log "预检: HDFS 输入 ${HDFS_INPUT}"
hdfs dfs -test -e "${HDFS_INPUT}" || die "HDFS 输入不存在: ${HDFS_INPUT}"

if [[ "${SKIP_ETL}" != "1" ]]; then
  [[ -n "${MYSQL_PASSWORD}" ]] || die "MYSQL_PASSWORD 为空，请检查 config/pipeline.env"
  log "预检: MySQL ${MYSQL_HOST}:${MYSQL_PORT}/${MYSQL_DATABASE}"
  if ! mysql -h "${MYSQL_HOST}" -P "${MYSQL_PORT}" -u"${MYSQL_USER}" -p"${MYSQL_PASSWORD}" \
      "${MYSQL_DATABASE}" -e "SELECT 1 AS ok;" 2>&1 | tee -a "${LOG_FILE}"; then
    die "无法连接 MySQL，请检查 Windows 防火墙、bind-address、allow_root_remote.sql"
  fi
  log "MySQL OK: ${MYSQL_HOST}"
fi

# --- MapReduce ---
if [[ "${SKIP_MR}" != "1" ]]; then
  JAR="${ROOT}/mapreduce/target/charging-mapreduce-1.0.0.jar"
  if [[ "${SKIP_BUILD}" != "1" && ( ! -f "${JAR}" || "${ROOT}/mapreduce/pom.xml" -nt "${JAR}" ) ]]; then
    log "编译 MapReduce ..."
    (cd "${ROOT}/mapreduce" && mvn -q clean package -DskipTests) | tee -a "${LOG_FILE}"
  fi
  [[ -f "${JAR}" ]] || die "Jar 不存在: ${JAR}"

  log "执行 MapReduce JobRunner: ${HDFS_INPUT} -> ${HDFS_OUTPUT_BASE}"
  hadoop jar "${JAR}" "${HDFS_INPUT}" "${HDFS_OUTPUT_BASE}" 2>&1 | tee -a "${LOG_FILE}"

  log "校验 HDFS 输出 v1~v7"
  for v in v1 v2 v3 v4 v5 v6 v7; do
    hdfs dfs -test -e "${HDFS_OUTPUT_BASE}/${v}/part-r-00000" || die "缺少输出 ${HDFS_OUTPUT_BASE}/${v}/part-r-00000"
  done
  log "MapReduce 完成"
else
  log "跳过 MapReduce (SKIP_MR=1)"
fi

# --- ETL 入库 ---
if [[ "${SKIP_ETL}" != "1" ]]; then
  log "ETL: HDFS ${HDFS_OUTPUT_BASE} -> MySQL ${MYSQL_HOST}/${MYSQL_DATABASE}"
  python3 "${ROOT}/analytics/scripts/load_mr_to_mysql.py" \
    --env-file "${ENV_FILE}" \
    --hdfs-base "${HDFS_OUTPUT_BASE}" 2>&1 | tee -a "${LOG_FILE}"
  log "ETL 完成"
else
  log "跳过 ETL (SKIP_ETL=1)"
fi

# --- ADS 汇总（Spark：dsv13r2 电池 + nvv2t 充电行为）---
if [[ "${SKIP_ADS}" != "1" && "${SKIP_ETL}" != "1" ]]; then
  HDFS_ADS_DSV="${HDFS_ADS_DSV:-/Car/dsv13r2.csv}"
  HDFS_ADS_NVV="${HDFS_ADS_NVV:-/Car/nvv2t.csv}"
  hdfs dfs -test -e "${HDFS_ADS_DSV}" || die "ADS 需要: ${HDFS_ADS_DSV}"
  hdfs dfs -test -e "${HDFS_ADS_NVV}" || die "ADS 需要: ${HDFS_ADS_NVV}"

  log "ADS ETL (Spark): dsv13r2 + nvv2t -> MySQL ADS"
  bash "${ROOT}/spark/scripts/run-spark-ads.sh" \
    --dsv13r2 "${HDFS_ADS_DSV}" \
    --nvv2t "${HDFS_ADS_NVV}" 2>&1 | tee -a "${LOG_FILE}"
  log "ADS ETL 完成"
else
  log "跳过 ADS ETL (SKIP_ADS=1 或 SKIP_ETL=1)"
fi

# --- 通知后端清空 BI 缓存 ---
if [[ "${SKIP_ETL}" != "1" ]]; then
  BACKEND_URL="${BACKEND_URL:-http://127.0.0.1:8000}"
  PIPELINE_SECRET="${PIPELINE_SECRET:-charging-pipeline-dev}"
  log "通知后端清空 BI 缓存: ${BACKEND_URL}"
  if curl -sf -X POST "${BACKEND_URL}/api/v1/bi/cache/invalidate-pipeline" \
      -H "X-Pipeline-Secret: ${PIPELINE_SECRET}" >/dev/null; then
    log "BI 缓存已失效"
  else
    log "WARN: 无法通知后端清 BI 缓存（后端未启动可忽略）"
  fi
fi

log "========== 流水线 SUCCESS =========="
