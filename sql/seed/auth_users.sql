-- 重置演示账号（服务器 MySQL 已存在错误/未验证记录时使用）
-- 用法（在 ~/charging-bigdata 目录）：
--   docker compose exec -T mysql mysql -uroot -p"$MYSQL_ROOT_PASSWORD" charging_bigdata < sql/seed/auth_users.sql

USE charging_bigdata;

INSERT INTO sys_user (username, email, password_hash, role, is_active, email_verified) VALUES
('admin', 'admin@example.com', '$2b$12$1kbXiQijwATCTwFL2lFNAOBkdKPhZyKDDENxdpVw0xK/3jNvDGgY6', 'admin', 1, 1),
('user',  'user@example.com',  '$2b$12$yfXdLvMo5tKwpw.Lo6Js8.lz/ZPXBJoMUsqt/JKIB39N.oJJe1r9G', 'user',  1, 1)
ON DUPLICATE KEY UPDATE
  email = VALUES(email),
  password_hash = VALUES(password_hash),
  role = VALUES(role),
  is_active = VALUES(is_active),
  email_verified = 1;
