-- BI 图表视图配置（Phase B：对标 Davinci v3 数据视图）
-- 执行：mysql -h 127.0.0.1 -uroot -p charging_bigdata < view_config_schema.sql

USE charging_bigdata;

CREATE TABLE IF NOT EXISTS bi_chart_view (
    id INT AUTO_INCREMENT PRIMARY KEY,
    chart_key VARCHAR(16) NOT NULL COMMENT '图表键 v1/p1 等',
    title VARCHAR(128) NOT NULL,
    chart_type VARCHAR(32) NOT NULL COMMENT 'line|bar|scatter|pie|heatmap',
    data_source VARCHAR(128) NOT NULL COMMENT 'API 或表',
    drill_route VARCHAR(64) DEFAULT NULL COMMENT '下钻路由',
    grid_area VARCHAR(16) DEFAULT NULL,
    sort_order INT NOT NULL DEFAULT 0,
    enabled TINYINT(1) NOT NULL DEFAULT 1,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_chart_key (chart_key)
) COMMENT 'BI 图表视图配置';
