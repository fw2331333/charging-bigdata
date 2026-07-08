-- 已有库升级：增加 Refresh Token 表（双 Token 机制）
-- 执行：mysql -uroot -p charging_bigdata < sql/migrations/002_refresh_token.sql

USE charging_bigdata;

CREATE TABLE IF NOT EXISTS sys_refresh_token (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL COMMENT '所属用户',
    token_hash VARCHAR(64) NOT NULL COMMENT 'Refresh Token SHA256 哈希',
    expires_at DATETIME NOT NULL COMMENT '过期时间',
    revoked TINYINT(1) NOT NULL DEFAULT 0 COMMENT '1已吊销 0有效',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_token_hash (token_hash),
    KEY idx_username (username),
    KEY idx_expires (expires_at)
) COMMENT 'Refresh Token 存储（服务端轮换）';
