#!/usr/bin/env python3
"""在 backend 容器内生成演示账号 bcrypt 哈希（供 SQL 更新）。"""
from app.core.security import hash_password, verify_password

SEED_ADMIN = "$2b$12$1kbXiQijwATCTwFL2lFNAOBkdKPhZyKDDENxdpVw0xK/3jNvDGgY6"
admin_hash = hash_password("admin123")
user_hash = hash_password("user123")
print("verify_seed_admin:", verify_password("admin123", SEED_ADMIN))
print("ADMIN_HASH=" + admin_hash)
print("USER_HASH=" + user_hash)
