-- 为用户表增加邮箱字段
USE charging_bigdata;

ALTER TABLE sys_user
  ADD COLUMN email VARCHAR(100) NULL COMMENT '登录邮箱' AFTER username;

ALTER TABLE sys_user
  ADD UNIQUE KEY uk_email (email);

UPDATE sys_user SET email = 'admin@example.com' WHERE username = 'admin';
UPDATE sys_user SET email = 'user@example.com' WHERE username = 'user';
