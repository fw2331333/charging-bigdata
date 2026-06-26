-- Hive ODS 明细层：外部表映射 HDFS 原始 CSV
-- 使用前在 VM 执行: bash hive/scripts/prepare_ods_paths.sh

CREATE DATABASE IF NOT EXISTS charging_ods;
USE charging_ods;

DROP TABLE IF EXISTS ods_dsv13r1;
CREATE EXTERNAL TABLE ods_dsv13r1 (
    id STRING,
    record_time STRING,
    soc DOUBLE,
    pack_voltage DOUBLE,
    charge_current DOUBLE,
    max_cell_voltage DOUBLE,
    min_cell_voltage DOUBLE,
    max_temperature DOUBLE,
    min_temperature DOUBLE,
    available_energy DOUBLE,
    available_capacity DOUBLE
)
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/warehouse/ods/dsv13r1';

DROP TABLE IF EXISTS ods_dsv13r2;
CREATE EXTERNAL TABLE ods_dsv13r2 (
    id STRING,
    record_time STRING,
    soc DOUBLE
)
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/warehouse/ods/dsv13r2';

DROP TABLE IF EXISTS ods_nvv2t;
CREATE EXTERNAL TABLE ods_nvv2t (
    id STRING,
    station_id STRING,
    pile_id STRING,
    created_time STRING,
    extra STRING
)
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/warehouse/ods/nvv2t';

-- ADS 汇总示例（Hive 内计算，结果可导出到 MySQL）
-- INSERT OVERWRITE LOCAL DIRECTORY '/tmp/ads_soc' ...
-- 本项目由 Spark SQL（load_ads_spark.py）从 HDFS 读明细并写入 MySQL ADS
