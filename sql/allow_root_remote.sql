-- Windows MySQL：允许虚拟机通过 NAT(10.0.2.x) 用 root 入库
-- 在 Windows CMD 执行：mysql -uroot -p123456 < allow_root_remote.sql

CREATE DATABASE IF NOT EXISTS charging_bigdata DEFAULT CHARSET utf8mb4;

-- MySQL 8.x
CREATE USER IF NOT EXISTS 'root'@'%' IDENTIFIED BY '123456';
GRANT ALL PRIVILEGES ON charging_bigdata.* TO 'root'@'%';
GRANT ALL PRIVILEGES ON charging_bigdata.* TO 'root'@'localhost';

FLUSH PRIVILEGES;
