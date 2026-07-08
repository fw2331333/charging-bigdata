-- 演示账号（邮箱登录）
USE charging_bigdata;

INSERT INTO sys_user (username, email, password_hash, role, is_active) VALUES
('admin', 'admin@example.com', '$2b$12$1kbXiQijwATCTwFL2lFNAOBkdKPhZyKDDENxdpVw0xK/3jNvDGgY6', 'admin', 1),
('user',  'user@example.com',  '$2b$12$yfXdLvMo5tKwpw.Lo6Js8.lz/ZPXBJoMUsqt/JKIB39N.oJJe1r9G', 'user',  1)
ON DUPLICATE KEY UPDATE
  email = VALUES(email),
  password_hash = VALUES(password_hash),
  role = VALUES(role),
  is_active = VALUES(is_active);
