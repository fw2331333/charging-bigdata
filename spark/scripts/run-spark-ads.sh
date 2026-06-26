#!/bin/bash
# Spark SQL ADS 入库 MySQL
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ENV_FILE="${ROOT}/config/pipeline.env"
JAR_DIR="${ROOT}/spark/jars"
JDBC_JAR="${MYSQL_JDBC_JAR:-}"

export SPARK_HOME="${SPARK_HOME:-/usr/local/spark}"
export JAVA_HOME="${JAVA_HOME:-/usr/local/jdk1.8.0_162}"
export HADOOP_HOME="${HADOOP_HOME:-/usr/local/hadoop}"
export PATH="${JAVA_HOME}/bin:${SPARK_HOME}/bin:${HADOOP_HOME}/bin:${PATH}"

if [[ -z "${JDBC_JAR}" ]]; then
  JDBC_JAR="$(ls "${JAR_DIR}"/mysql-connector-j-*.jar "${JAR_DIR}"/mysql-connector-java-*.jar 2>/dev/null | head -1 || true)"
fi
[[ -n "${JDBC_JAR}" && -f "${JDBC_JAR}" ]] || {
  echo "ERROR: 缺少 MySQL JDBC 驱动，请放到 ${JAR_DIR}/"
  echo "  wget -P ${JAR_DIR} https://repo1.maven.org/maven2/com/mysql/mysql-connector-j/8.0.33/mysql-connector-j-8.0.33.jar"
  exit 1
}

[[ -f "${ENV_FILE}" ]] || { echo "ERROR: 缺少 ${ENV_FILE}"; exit 1; }

echo "==> Spark SQL ADS -> MySQL"
spark-submit \
  --master "${SPARK_MASTER:-local[*]}" \
  --driver-memory "${SPARK_DRIVER_MEMORY:-1g}" \
  --jars "${JDBC_JAR}" \
  "${ROOT}/spark/scripts/load_ads_spark.py" \
  --env-file "${ENV_FILE}" \
  "$@"
