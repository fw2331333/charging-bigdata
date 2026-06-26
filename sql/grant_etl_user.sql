-- 在 Windows MySQL 上执行，允许虚拟机 ETL 用户远程入库
-- mysql -uroot -p < grant_etl_user.sql

CREATE DATABASE IF NOT EXISTS charging_bigdata DEFAULT CHARSET utf8mb4;

CREATE USER IF NOT EXISTS 'cbp_etl'@'%' IDENTIFIED BY '请改成与 pipeline.env 一致的密码';
GRANT SELECT, INSERT, UPDATE, DELETE ON charging_bigdata.* TO 'cbp_etl'@'%';
FLUSH PRIVILEGES;
