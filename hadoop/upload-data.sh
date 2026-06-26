#!/bin/bash
# 上传项目 CSV 到 HDFS /Car/（指导书 §5.1 四个文件）
# 日常请用 scripts/vm-setup-once.sh（自动调用本脚本）
# 手动：bash hadoop/upload-data.sh /media/sf_cs-/dataset
set -euo pipefail

DATA_DIR="${1:-}"
HDFS_DIR="/Car"

if [[ -z "${DATA_DIR}" || ! -d "${DATA_DIR}" ]]; then
  echo "用法: bash upload-data.sh <本地CSV目录>"
  echo "示例: bash upload-data.sh /home/hadoop/dataset"
  exit 1
fi

source /etc/profile.d/hadoop.sh 2>/dev/null || true

FILES=(dsv13r1.csv dsv13r2.csv nvv2t.csv nvv2t_md.csv)
hdfs dfs -mkdir -p "${HDFS_DIR}"

for f in "${FILES[@]}"; do
  src="${DATA_DIR}/${f}"
  if [[ ! -f "${src}" ]]; then
    echo "[WARN] 缺少文件: ${src}"
    continue
  fi
  echo "上传 ${f} ..."
  hdfs dfs -put -f "${src}" "${HDFS_DIR}/${f}"
done

echo ""
echo "==> HDFS 文件列表"
hdfs dfs -ls "${HDFS_DIR}"
echo ""
echo "==> dsv13r1 前 3 行（MapReduce 输入）"
hdfs dfs -cat "${HDFS_DIR}/dsv13r1.csv" | head -3
