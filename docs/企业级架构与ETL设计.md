# 企业级架构与 ETL 设计

本文说明本项目为何采用 **「计算与入库分离」** 的 ETL 模式，以及如何与课程评分表、三节点 Hadoop 集群对齐。

---

## 1. 分层架构

```text
┌─────────────────────────────────────────────────────────────────┐
│  展示层    Vue3 + ECharts（只调 REST API）                        │
├─────────────────────────────────────────────────────────────────┤
│  服务层    FastAPI（只读 MySQL，不依赖 Hadoop 在线）               │
├─────────────────────────────────────────────────────────────────┤
│  服务层 DB  MySQL charging_bigdata（MR 表 + ADS 表 + 可选模型）    │
├─────────────────────────────────────────────────────────────────┤
│  ETL 层    load_mr_to_mysql.py / load_ads_spark.py（幂等写入）     │
├─────────────────────────────────────────────────────────────────┤
│  计算层    MapReduce v1~v7（HDFS 输出）+ Spark ADS               │
├─────────────────────────────────────────────────────────────────┤
│  存储层    HDFS /Car/*.csv（ODS，副本数 1→3）                      │
└─────────────────────────────────────────────────────────────────┘
```

| 层级 | 职责 | 本项目实现 |
|------|------|------------|
| ODS | 原始数据落地 | HDFS `/Car/` 四个 CSV |
| DWD/DWS | 分布式统计 | MR v1~v7、Spark ADS |
| ADS / 服务表 | 面向查询的窄表 | MySQL `t_*` |
| API | 统一数据出口 | FastAPI `/api/v1` |
| UI | 可视化 | Vue + ECharts |

---

## 2. 为何坚持 ETL，而非 MapReduce Reducer 写 MySQL

课程评分表可能出现「MapReduce 访问 MySQL」字样；**企业生产环境更常见做法如下**：

| 对比项 | MR Reducer 直连 JDBC | 独立 ETL（本项目） |
|--------|----------------------|-------------------|
| 职责 | 计算与入库耦合 | **单一职责**：MR 只负责统计 |
| 失败恢复 | 任务失败可能导致部分写入 | HDFS 结果保留，ETL 可单独重跑 |
| 连接数 | 每个 Reducer 持连接，易打满 DB | 单进程批量写入，可控 |
| 幂等 | 需自行处理重复键 | `ON DUPLICATE KEY UPDATE` 统一策略 |
| 安全 | 集群节点需 DB 账号与网络放通 | 仅 ETL 节点访问 MySQL |
| 扩展 | 换库（ClickHouse/Doris）需改 Java | 只改 ETL 脚本 |

**答辩表述建议**：

> MapReduce 负责海量数据的分布式聚合，结果落地 HDFS；由独立 ETL 进程将 `part-r-00000` 幂等导入 MySQL 服务层，Web 与 API 只读 MySQL。这与数据中台「离线计算 + 服务层」的分工一致。

代码位置：

- ETL 包：`analytics/etl/`
- CLI：`analytics/scripts/load_mr_to_mysql.py`
- 流水线编排：`scripts/run-pipeline.sh`

---

## 3. 三节点真分布式

### 拓扑

```text
hadoop-master   NameNode + ResourceManager + DataNode + NodeManager
hadoop-slave1   DataNode + NodeManager
hadoop-slave2   DataNode + NodeManager

Windows 宿主机  MySQL 8（服务层，10.0.2.2 或实验室 IP）
```

### 配置文件（评分表「8 大配置」对照）

| 文件 | 路径 | 说明 |
|------|------|------|
| core-site.xml | `hadoop/conf-cluster/` | `fs.defaultFS=hdfs://hadoop-master:9000` |
| hdfs-site.xml | 同上 | `dfs.replication=3` |
| yarn-site.xml | 同上 | RM 主机名 |
| mapred-site.xml | 同上 | YARN 模式 |
| workers | 同上 | 三台 DN/NM |
| hadoop-env.sh | 同上 | JVM 堆参数 |
| hadoop-env（安装） | `/etc/profile.d/hadoop.sh` | JAVA_HOME、HADOOP_HOME |
| SSH 免密 | `hadoop/cluster/setup-ssh-cluster.sh` | start-dfs 远程启动依赖 |

### 部署步骤摘要

详见 [三节点集群部署手册.md](./三节点集群部署手册.md)。

```bash
# 1. 三台 /etc/hosts（见 hadoop/cluster/cluster-hosts.example）
# 2. Master 上 hadoop 用户 SSH 免密
bash hadoop/cluster/setup-ssh-cluster.sh
# 3. 同步配置
export HADOOP_HOME=/opt/hadoop-3.1.3
bash hadoop/cluster/deploy-cluster-config.sh
# 4. 启动与验证
start-dfs.sh && start-yarn.sh
bash hadoop/cluster/verify-cluster.sh
# 5. 业务流水线（与单机相同）
bash scripts/run-pipeline.sh
```

扩集群后 **Java MR 代码与 Web 无需修改**；副本数提升后 HDFS 自动多副本。

---

## 4. 离线流水线（单入口）

`scripts/run-pipeline.sh` 阶段：

1. **Preflight** — Hadoop、HDFS 输入、MySQL 连通性
2. **MapReduce** — `JobRunner` v1~v7 → `/Car/output/v*`
3. **ETL** — `load_mr_to_mysql.py` → MySQL MR 表
4. **ADS** — Spark `load_ads_spark.py` → MySQL ADS 表

跳过开关（`config/pipeline.env`）：`SKIP_MR` / `SKIP_ETL` / `SKIP_ADS` / `SKIP_BUILD`。

---

## 5. Web 服务层（与 Hadoop 解耦）

演示模式：`sql/seed/charging_bigdata_data.sql` → MySQL → API → 前端。

生产模式：流水线写入同一套表结构，API 无感知。

后端分层：

```text
api/v1/endpoints  →  HTTP 路由、参数校验
services          →  业务编排
repositories      →  SQL 访问
schemas           →  Pydantic 响应模型
core              →  配置、连接池、常量
```

---

## 6. 评分表自评对照（技术项）

| 评分项 | 本项目对应 |
|--------|------------|
| Linux 分布式环境 | 三节点 + `verify-cluster.sh` |
| SSH 免密 | `setup-ssh-cluster.sh` |
| Hadoop 8 大配置 | `conf-cluster/` 全套 + `hadoop-env.sh` |
| HDFS / YARN Web | 9870 / 8088 |
| MR 正确运行 | v1~v7 + `JobRunner` |
| MR → MySQL | **ETL 层**（企业实践，见 §2） |
| ML 配置 | `train_all_models.py` + `.pkl` |
| API | FastAPI `/docs` |
| 多层架构 | §1 分层图 |

---

## 相关文档

- [三节点集群部署手册.md](./三节点集群部署手册.md)
- [虚拟机一次性运行手册.md](./虚拟机一次性运行手册.md)
- [离线批处理流水线.md](./离线批处理流水线.md)
- [hadoop/README.md](../hadoop/README.md)
