-- 新能源充电桩大数据项目 MapReduce 结果表
-- 数据库名可按需修改

CREATE DATABASE IF NOT EXISTS charging_bigdata DEFAULT CHARSET utf8mb4;
USE charging_bigdata;

-- v1 每小时平均组电压和平均充电电流
CREATE TABLE IF NOT EXISTS t_voltage_current (
    id INT AUTO_INCREMENT PRIMARY KEY,
    record_hour VARCHAR(20) NOT NULL COMMENT 'yyyyMMddHH',
    avg_pack_voltage DOUBLE COMMENT '平均组电压(V)',
    avg_charge_current DOUBLE COMMENT '平均充电电流(A)',
    UNIQUE KEY uk_record_hour (record_hour)
) COMMENT 'v1-电压电流趋势';

-- v2 单体电压范围（每小时最高单体电压、最低单体电压）
CREATE TABLE IF NOT EXISTS t_cell_voltage_range (
    id INT AUTO_INCREMENT PRIMARY KEY,
    record_hour VARCHAR(20) NOT NULL COMMENT 'yyyyMMddHH',
    max_cell_voltage DOUBLE COMMENT '最高单体电压(V)',
    min_cell_voltage DOUBLE COMMENT '最低单体电压(V)',
    UNIQUE KEY uk_record_hour (record_hour)
) COMMENT 'v2-单体电压范围';

-- v3 每个时间点最高/最低温度
CREATE TABLE IF NOT EXISTS t_temperature (
    id INT AUTO_INCREMENT PRIMARY KEY,
    record_time VARCHAR(20) NOT NULL COMMENT 'yyyyMMddHHmmss',
    max_temperature DOUBLE COMMENT '最高温度(℃)',
    min_temperature DOUBLE COMMENT '最低温度(℃)',
    UNIQUE KEY uk_record_time (record_time)
) COMMENT 'v3-温度趋势';

-- v4 可用能量和可用容量趋势（每小时平均）
CREATE TABLE IF NOT EXISTS t_energy_capacity (
    id INT AUTO_INCREMENT PRIMARY KEY,
    record_hour VARCHAR(20) NOT NULL COMMENT 'yyyyMMddHH',
    avg_available_energy DOUBLE COMMENT '平均可用能量(kw)',
    avg_available_capacity DOUBLE COMMENT '平均可用容量(Ah)',
    UNIQUE KEY uk_record_hour (record_hour)
) COMMENT 'v4-能量容量趋势';

-- v5 平均/最大充电电流
CREATE TABLE IF NOT EXISTS t_charge_current_stats (
    id INT AUTO_INCREMENT PRIMARY KEY,
    record_hour VARCHAR(20) NOT NULL COMMENT 'yyyyMMddHH',
    avg_charge_current DOUBLE COMMENT '平均充电电流(A)',
    max_charge_current DOUBLE COMMENT '最大充电电流(A)',
    UNIQUE KEY uk_record_hour (record_hour)
) COMMENT 'v5-充电电流统计';

-- v6 组电压与充电电流关系（每个时间点）
CREATE TABLE IF NOT EXISTS t_voltage_current_relation (
    id INT AUTO_INCREMENT PRIMARY KEY,
    record_time VARCHAR(20) NOT NULL COMMENT 'yyyyMMddHHmmss',
    pack_voltage DOUBLE COMMENT '组电压(V)',
    charge_current DOUBLE COMMENT '充电电流(A)',
    UNIQUE KEY uk_record_time (record_time)
) COMMENT 'v6-电压电流关系';

-- v7 不同电池状态(SOC分段)下平均最高/最低温度
CREATE TABLE IF NOT EXISTS t_soc_temperature (
    id INT AUTO_INCREMENT PRIMARY KEY,
    soc_bucket VARCHAR(20) NOT NULL COMMENT 'SOC分段，如10-20',
    avg_max_temperature DOUBLE COMMENT '平均最高温度(℃)',
    avg_min_temperature DOUBLE COMMENT '平均最低温度(℃)',
    UNIQUE KEY uk_soc_bucket (soc_bucket)
) COMMENT 'v7-电池状态温度';

-- BI 视图示例
CREATE OR REPLACE VIEW v_voltage_current AS
SELECT record_hour, avg_pack_voltage, avg_charge_current FROM t_voltage_current;

CREATE OR REPLACE VIEW v_temperature AS
SELECT record_time, max_temperature, min_temperature FROM t_temperature;

CREATE OR REPLACE VIEW v_soc_temperature AS
SELECT soc_bucket, avg_max_temperature, avg_min_temperature FROM t_soc_temperature;
