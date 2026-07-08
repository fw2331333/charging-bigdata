#!/usr/bin/env bash
# 校验 GitHub / 服务器部署所需文件是否齐全
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

REQUIRED=(
  docker-compose.yml
  .env.docker.example
  docker/README.md
  docker/mysql/03-seed.sh
  sql/schema.sql
  sql/ads_schema.sql
  sql/auth_schema.sql
  sql/view_config_schema.sql
  sql/migrations/004_email_verification.sql
  sql/migrations/005_profile_otp.sql
  sql/seed/charging_bigdata_data.sql
  sql/seed/auth_users.sql
  backend/Dockerfile
  backend/requirements.txt
  backend/main.py
  backend/app/main.py
  frontend/Dockerfile
  frontend/nginx.conf
  frontend/package.json
  frontend/package-lock.json
  frontend/src/main.ts
  analytics/output/models/.gitkeep
)

OPTIONAL=(
  docker-compose.datart.yml
  analytics/output/models/metrics.json
  analytics/output/models/performance_report.json
  analytics/output/models/fee_model.pkl
  analytics/output/models/duration_model.pkl
  analytics/output/models/platform_model.pkl
  analytics/output/models/soc_model.pkl
)

FORBIDDEN=(
  .env
  backend/.env
  config/pipeline.env
)

missing=0
for f in "${REQUIRED[@]}"; do
  if [[ ! -e "$f" ]]; then
    echo "[缺失] $f"
    missing=1
  fi
done

echo ""
echo "可选文件（预测 / Datart）："
for f in "${OPTIONAL[@]}"; do
  if [[ -e "$f" ]]; then
    echo "  [有] $f"
  else
    echo "  [无] $f"
  fi
done

echo ""
echo "敏感文件（不应提交 Git）："
for f in "${FORBIDDEN[@]}"; do
  if [[ -e "$f" ]]; then
    if git check-ignore -q "$f" 2>/dev/null; then
      echo "  [已忽略] $f"
    else
      echo "  [警告] $f 存在但未在 .gitignore 中"
      missing=1
    fi
  fi
done

echo ""
if [[ "$missing" -eq 0 ]]; then
  echo "部署必需文件检查通过。"
  exit 0
fi
echo "存在缺失或风险项，请按 docs/服务器部署与GitHub目录.md 补齐。"
exit 1
