-- MySQL ADS 应用层：探索分析汇总（供大屏 API 只读）
-- 明细在 HDFS，由 Spark SQL（load_ads_spark.py）聚合写入

USE charging_bigdata;

CREATE TABLE IF NOT EXISTS t_soc_hourly (
    id INT AUTO_INCREMENT PRIMARY KEY,
    time_key VARCHAR(20) NOT NULL COMMENT 'yyyyMMddHH，按时间正序展示',
    avg_soc DOUBLE NOT NULL,
    UNIQUE KEY uk_time_key (time_key)
) COMMENT 'ADS-每小时平均SOC';

CREATE TABLE IF NOT EXISTS t_charging_daily (
    id INT AUTO_INCREMENT PRIMARY KEY,
    record_date VARCHAR(10) NOT NULL COMMENT 'yyyyMMdd',
    charge_count INT NOT NULL,
    UNIQUE KEY uk_record_date (record_date)
) COMMENT 'ADS-每日充电次数';

CREATE TABLE IF NOT EXISTS t_charging_monthly (
    id INT AUTO_INCREMENT PRIMARY KEY,
    record_month VARCHAR(7) NOT NULL COMMENT 'yyyyMM',
    charge_count INT NOT NULL,
    UNIQUE KEY uk_record_month (record_month)
) COMMENT 'ADS-每月充电次数';

CREATE TABLE IF NOT EXISTS t_charge_rate_hourly (
    id INT AUTO_INCREMENT PRIMARY KEY,
    hour_key VARCHAR(4) NOT NULL COMMENT 'HH',
    avg_rate DOUBLE NOT NULL COMMENT '%%SOC/分钟',
    UNIQUE KEY uk_hour_key (hour_key)
) COMMENT 'ADS-每小时平均充电速率';

CREATE TABLE IF NOT EXISTS t_soc_heatmap (
    id INT AUTO_INCREMENT PRIMARY KEY,
    record_day VARCHAR(10) NOT NULL COMMENT 'yyyyMMdd',
    hour_key VARCHAR(4) NOT NULL COMMENT 'HH',
    avg_soc DOUBLE NOT NULL,
    UNIQUE KEY uk_day_hour (record_day, hour_key)
) COMMENT 'ADS-SOC热力图';
