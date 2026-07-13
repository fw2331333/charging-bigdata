/**
 * 新能源充电桩 MapReduce 统计模块（v1~v7）。
 *
 * <p>企业级数据流：
 * <pre>
 *   HDFS /Car/dsv13r1.csv
 *       → MapReduce（本模块，只写 HDFS 分区结果）
 *       → 独立 ETL（analytics/etl，幂等写入 MySQL）
 *       → FastAPI 只读服务层
 * </pre>
 *
 * <p>包结构：
 * <ul>
 *   <li>{@link com.cbp.mr.JobRunner} — 批量编排入口</li>
 *   <li>{@code v1..v7} — 各统计任务（Mapper/Reducer）</li>
 *   <li>{@code util} — 解析、聚合、Job 构建公共逻辑</li>
 * </ul>
 */
package com.cbp.mr;
