#!/usr/bin/env bash
# 服务器 git pull 后更新 Web 演示（对齐 docs/服务器部署与GitHub目录.md）
# 用法：cd ~/charging-bigdata && bash scripts/server-update-web.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

ENV_FILE="${ENV_FILE:-.env.docker}"
if [[ ! -f "$ENV_FILE" ]]; then
  cp .env.docker.example "$ENV_FILE"
  echo "[ok] 已创建 $ENV_FILE（请确认 PUBLIC_HOST / MYSQL_ROOT_PASSWORD）"
fi

MYSQL_PW="$(grep -E '^MYSQL_ROOT_PASSWORD=' "$ENV_FILE" | cut -d= -f2- || true)"
MYSQL_PW="${MYSQL_PW:-charging123}"

echo "[1/5] git pull ..."
git pull origin main
echo "      HEAD: $(git log -1 --oneline)"

echo "[2/5] 重建 backend + frontend ..."
docker compose --env-file "$ENV_FILE" up -d --build backend frontend

echo "[3/5] 等待 MySQL healthy ..."
for _ in $(seq 1 30); do
  if docker exec cbp-mysql mysqladmin ping -h127.0.0.1 -uroot -p"$MYSQL_PW" --silent 2>/dev/null; then
    break
  fi
  sleep 2
done

echo "[4/5] 强制写入 v6/v7 种子（绕过旧表结构/缓存）..."
if [[ -f sql/seed/v6_v7_data.sql ]]; then
  docker exec -i cbp-mysql mysql -uroot -p"$MYSQL_PW" charging_bigdata < sql/seed/v6_v7_data.sql
else
  echo "      警告: sql/seed/v6_v7_data.sql 不存在，跳过"
fi

echo "[5/5] 重启 backend 并检查 ..."
docker restart cbp-backend >/dev/null
sleep 5

echo ""
echo "=== backend 启动日志（v6/v7）==="
docker logs cbp-backend 2>&1 | grep -E "v6/v7|schema still old|seed" | tail -5 || true

echo ""
echo "=== t_voltage_current_relation ==="
docker exec cbp-mysql mysql -uroot -p"$MYSQL_PW" charging_bigdata \
  -e "SELECT record_hour, voltage_change_rate, current_change_rate FROM t_voltage_current_relation ORDER BY record_hour;"

echo ""
echo "=== 完成 ==="
echo "浏览器强制刷新: http://<公网IP>:8080/mr-bi  (Ctrl+Shift+R)"
echo "v6 新数据 hour00 电流约 -0.019333；11-14 仍为 0（数据集 |I| 恒为 22.5A）"
