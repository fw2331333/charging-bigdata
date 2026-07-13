#!/usr/bin/env bash
# 单独启动 Datart BI（手册 §5.2）
set -euo pipefail

PORT="${1:-8088}"
NAME="${DATART_CONTAINER_NAME:-cbp-datart}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CONF="${ROOT}/docker/datart/datart.conf"

if docker ps -a --format '{{.Names}}' | grep -qx "$NAME"; then
  docker rm -f "$NAME" >/dev/null
fi

echo "启动 Datart → http://127.0.0.1:${PORT} （默认账号 demo/123456）"
docker run -d \
  --name "$NAME" \
  -p "${PORT}:8080" \
  -v "${CONF}:/datart/config/datart.conf" \
  -v cbp_datart_files:/datart/files \
  datart/datart

echo "完成。配置业务数据源见 docs/Datart-BI大屏部署手册.md"
