-- 个人资料：邮箱验证码（修改密码等）
-- mysql -uroot -p charging_bigdata < sql/migrations/005_profile_otp.sql

USE charging_bigdata;

CREATE TABLE IF NOT EXISTS sys_profile_otp (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL COMMENT 'sys_user.id',
    code_hash VARCHAR(64) NOT NULL COMMENT '验证码 SHA256',
    purpose VARCHAR(32) NOT NULL DEFAULT 'change_password',
    expires_at DATETIME NOT NULL,
    used TINYINT(1) NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    KEY idx_user_purpose (user_id, purpose),
    KEY idx_expires (expires_at)
) COMMENT '个人资料操作邮箱验证码';
