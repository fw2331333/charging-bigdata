# 加载 config/pipeline.env（自动去除 Windows CRLF）
# 用法: source "${ROOT}/scripts/lib/source-env.sh"
: "${ENV_FILE:?ENV_FILE 未设置}"

if [[ ! -f "${ENV_FILE}" ]]; then
  echo "ERROR: 缺少 ${ENV_FILE}" >&2
  return 1 2>/dev/null || exit 1
fi

# 共享文件夹下常为 CRLF；必须在 source 之前去掉 \r
if grep -q $'\r' "${ENV_FILE}" 2>/dev/null; then
  sed -i 's/\r$//' "${ENV_FILE}" 2>/dev/null || sed -i '' 's/\r$//' "${ENV_FILE}" 2>/dev/null || true
fi

# shellcheck disable=SC1090
source "${ENV_FILE}"

for _k in MYSQL_HOST MYSQL_PORT MYSQL_USER MYSQL_PASSWORD MYSQL_DATABASE \
  HADOOP_HOME JAVA_HOME SPARK_HOME HDFS_INPUT HDFS_OUTPUT_BASE \
  HDFS_ADS_DSV HDFS_ADS_NVV DATASET_LOCAL_DIR MYSQL_JDBC_JAR \
  SKIP_MR SKIP_ETL SKIP_BUILD SKIP_ADS SPARK_MASTER SPARK_DRIVER_MEMORY; do
  if [[ -n "${!_k:-}" ]]; then
    printf -v "$_k" '%s' "${!_k//$'\r'/}"
  fi
done
