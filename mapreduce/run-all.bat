@echo off
REM 在 Hadoop Master 节点执行（Git Bash 或 Linux 请用 run-all.sh）
set INPUT=%1
set OUTPUT=%2
set JAR=%3
if "%INPUT%"=="" set INPUT=/Car/dsv13r1.csv
if "%OUTPUT%"=="" set OUTPUT=/Car/output
if "%JAR%"=="" set JAR=target/charging-mapreduce-1.0.0.jar

call hadoop jar %JAR% com.cbp.mr.JobRunner %INPUT% %OUTPUT%
