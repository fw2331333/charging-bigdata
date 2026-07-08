-- 用户认证与授权表（与 charging_bigdata 业务库同库或独立 auth 库均可）
-- 执行：mysql -uroot -p charging_bigdata < auth_schema.sql

USE charging_bigdata;

-- 系统用户表
CREATE TABLE IF NOT EXISTS sys_user (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '用户ID',
    username VARCHAR(50) NOT NULL COMMENT '登录用户名',
    email VARCHAR(100) NULL COMMENT '登录邮箱',
    password_hash VARCHAR(255) NOT NULL COMMENT 'bcrypt 密码哈希，禁止存明文',
    role VARCHAR(20) NOT NULL DEFAULT 'user' COMMENT '角色：admin / user',
    is_active TINYINT(1) NOT NULL DEFAULT 1 COMMENT '1启用 0禁用',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    UNIQUE KEY uk_username (username),
    UNIQUE KEY uk_email (email),
    KEY idx_role (role)
) COMMENT '系统用户表';

-- 刷新令牌表（双 Token 机制：长期 Refresh + 短期 Access）
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

-- 可选：Access Token 黑名单（有状态登出扩展用）
CREATE TABLE IF NOT EXISTS sys_token_blacklist (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    token_jti VARCHAR(64) NOT NULL COMMENT 'JWT jti 唯一标识',
    expires_at DATETIME NOT NULL COMMENT '令牌过期时间',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_jti (token_jti)
) COMMENT 'JWT 黑名单（可选）';

-- 初始管理员需用应用生成 bcrypt 后替换下方哈希
-- python -c "from passlib.context import CryptContext; print(CryptContext(schemes=['bcrypt']).hash('admin123'))"
-- INSERT INTO sys_user (username, password_hash, role) VALUES ('admin', '<bcrypt_hash>', 'admin');
