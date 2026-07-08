-- 邮箱验证与密码重置令牌
-- mysql -uroot -p charging_bigdata < sql/migrations/004_email_verification.sql

USE charging_bigdata;

ALTER TABLE sys_user
    ADD COLUMN email_verified TINYINT(1) NOT NULL DEFAULT 1 COMMENT '1已验证 0待验证' AFTER is_active;

CREATE TABLE IF NOT EXISTS sys_email_verification_token (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL COMMENT 'sys_user.id',
    token_hash VARCHAR(64) NOT NULL COMMENT '令牌 SHA256',
    purpose VARCHAR(32) NOT NULL COMMENT 'verify_email / reset_password',
    expires_at DATETIME NOT NULL COMMENT '过期时间',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_token_hash (token_hash),
    KEY idx_user_purpose (user_id, purpose),
    KEY idx_expires (expires_at)
) COMMENT '邮箱验证 / 重置密码令牌';
