-- 对齐项目开发手册 §3.3.6 / §3.3.7：v6 变化率、v7 电池状态温度统计
-- 已有库执行：mysql charging_bigdata < sql/migrations/009_v6_v7_manual_align.sql

ALTER TABLE t_voltage_current_relation
    DROP INDEX uk_record_time;

ALTER TABLE t_voltage_current_relation
    CHANGE COLUMN record_time record_hour VARCHAR(20) NOT NULL COMMENT '小时 HH(00-23)',
    CHANGE COLUMN pack_voltage voltage_change_rate DOUBLE COMMENT '组电压变化率(%)',
    CHANGE COLUMN charge_current current_change_rate DOUBLE COMMENT '充电电流变化率(%)',
    ADD UNIQUE KEY uk_record_hour (record_hour);

ALTER TABLE t_soc_temperature
    DROP INDEX uk_soc_bucket;

ALTER TABLE t_soc_temperature
    CHANGE COLUMN soc_bucket battery_status VARCHAR(20) NOT NULL COMMENT 'idle/charging/discharging',
    ADD COLUMN var_max_temperature DOUBLE COMMENT '最高温度方差' AFTER avg_min_temperature,
    ADD COLUMN var_min_temperature DOUBLE COMMENT '最低温度方差' AFTER var_max_temperature,
    ADD UNIQUE KEY uk_battery_status (battery_status);

CREATE OR REPLACE VIEW v_soc_temperature AS
SELECT battery_status, avg_max_temperature, avg_min_temperature, var_max_temperature, var_min_temperature
FROM t_soc_temperature;
