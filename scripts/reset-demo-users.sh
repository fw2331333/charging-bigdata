#!/bin/bash
# 重置演示账号（在 ~/charging-bigdata 执行）
set -euo pipefail

ROOT_PASSWORD="${MYSQL_ROOT_PASSWORD:-Charging@2026}"

echo "== 当前 admin 记录 =="
docker compose exec mysql mysql -uroot -p"${ROOT_PASSWORD}" charging_bigdata -e \
  "SELECT id,username,email,email_verified,role FROM sys_user WHERE email='admin@example.com' OR username='admin';"

echo "== 生成新密码哈希 =="
eval "$(docker compose exec -T backend python /app/scripts/gen_demo_hashes.py 2>/dev/null || docker compose exec -T backend python -c "
from app.core.security import hash_password, verify_password
seed = '\$2b\$12\$1kbXiQijwATCTwFL2lFNAOBkdKPhZyKDDENxdpVw0xK/3jNvDGgY6'
print('verify_seed_admin:', verify_password('admin123', seed))
print('ADMIN_HASH=' + hash_password('admin123'))
print('USER_HASH=' + hash_password('user123'))
")"

docker compose exec mysql mysql -uroot -p"${ROOT_PASSWORD}" charging_bigdata -e "
DELETE FROM sys_refresh_token WHERE username IN ('admin','user');
INSERT INTO sys_user (username,email,password_hash,role,is_active,email_verified) VALUES
('admin','admin@example.com','${ADMIN_HASH}','admin',1,1),
('user','user@example.com','${USER_HASH}','user',1,1)
ON DUPLICATE KEY UPDATE
  email=VALUES(email),
  password_hash=VALUES(password_hash),
  role=VALUES(role),
  is_active=1,
  email_verified=1;
"

echo "== 登录接口测试 =="
curl -s -X POST http://127.0.0.1:8080/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"admin@example.com","password":"admin123"}'
echo
