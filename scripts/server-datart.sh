#!/usr/bin/env bash
# 服务器：启动 Datart + 修复七图 Dashboard + 输出分享链接
# 用法：cd ~/charging-bigdata && bash scripts/server-datart.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

ENV_FILE="${ENV_FILE:-.env.docker}"
COMPOSE="docker compose --env-file $ENV_FILE -f docker-compose.yml -f docker-compose.datart.yml"

if [[ ! -f "$ENV_FILE" ]]; then
  cp .env.docker.example "$ENV_FILE"
  echo "[ok] 已创建 $ENV_FILE"
fi

PUBLIC_HOST="$(grep -E '^PUBLIC_HOST=' "$ENV_FILE" | cut -d= -f2- || true)"
PUBLIC_HOST="${PUBLIC_HOST:-http://115.29.194.137:8080}"
HOST="$(echo "$PUBLIC_HOST" | sed -E 's|https?://([^:/]+).*|\1|')"
DATART_PUBLIC="http://${HOST}:8088"

echo "[1/4] 启动 Datart 容器 ..."
$COMPOSE up -d datart mysql
sleep 8

echo "[2/4] 等待 Datart 就绪 ..."
for _ in $(seq 1 30); do
  if curl -sf "http://127.0.0.1:8088/" >/dev/null 2>&1; then
    break
  fi
  sleep 2
done

echo "[3/4] 修复数据源 / 视图 / 七图 Dashboard ..."
export DATART_URL="http://127.0.0.1:8088"
bash "$ROOT/scripts/fix-datart-all.sh"

echo "[4/4] 重建 frontend（公网 Datart 地址）..."
if ! grep -q '^VITE_DATART_BASE_URL=' "$ENV_FILE"; then
  echo "VITE_DATART_BASE_URL=$DATART_PUBLIC" >>"$ENV_FILE"
else
  sed -i "s|^VITE_DATART_BASE_URL=.*|VITE_DATART_BASE_URL=$DATART_PUBLIC|" "$ENV_FILE"
fi

$COMPOSE up -d --build frontend

echo ""
echo "=== Datart BI 验收 ==="
echo "1. 浏览器打开: $DATART_PUBLIC"
echo "2. 登录 admin / 123456"
echo "3. 打开仪表板 Charging-BigData-BI（或 fix-datart-all 输出的 Share 链接）"
echo "4. 首页「Datart BI」按钮应指向 $DATART_PUBLIC"
echo ""
echo "若 8088 打不开：阿里云安全组放行 TCP 8088"
