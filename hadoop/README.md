# Hadoop 部署（单机 → 真三节点）

本目录提供 **Ubuntu/CentOS 伪分布式 → 三节点真集群** 的配置与脚本，与 MapReduce `3.1.3` 一致。**MR Java 代码与 Web 无需修改**。

## 推荐路线

```text
阶段 1  单机伪分布式（hadoop-master 一台承担全部角色）
阶段 2  真三节点（Master + 2 Slave，副本数 3，SSH 免密）
```

| 阶段 | 节点 | 角色 |
|------|------|------|
| 单机 | hadoop-master | NN + DN + RM + NM |
| 三节点 | hadoop-master | NN + RM + DN + NM |
| 三节点 | hadoop-slave1/2 | DN + NM |

**企业级数据流**（计算与入库分离）：MR 只写 HDFS → `analytics/etl` 幂等入 MySQL → FastAPI 只读。详见 [docs/企业级架构与ETL设计.md](../docs/企业级架构与ETL设计.md)。

---

## 阶段 1：单机安装

```bash
cd ~/charging-bigdata/hadoop
sudo bash install-pseudo-distributed.sh

sudo su - hadoop
source /etc/profile.d/hadoop.sh
start-dfs.sh && start-yarn.sh
```

- HDFS Web：`http://hadoop-master:9870`
- YARN Web：`http://hadoop-master:8088`
- 数据目录：`/data/hadoop`（与 `conf-pseudo/*.xml` 一致）
- `HADOOP_HOME`：`/opt/hadoop-3.1.3`

上传数据并验证 MR：

```bash
bash ~/charging-bigdata/hadoop/upload-data.sh /path/to/dataset
bash ~/charging-bigdata/hadoop/verify-mr.sh
```

全量流水线：

```bash
bash ~/charging-bigdata/scripts/vm-setup-once.sh   # 首次
bash ~/charging-bigdata/scripts/run-pipeline.sh  # MR → ETL → Spark ADS
```

---

## 阶段 2：真三节点集群

完整步骤见 **[docs/三节点集群部署手册.md](../docs/三节点集群部署手册.md)**。

```bash
# 1. 三台 /etc/hosts（hadoop/cluster/cluster-hosts.example）
# 2. SSH 免密（hadoop 用户，在 Master 执行）
bash hadoop/cluster/setup-ssh-cluster.sh

# 3. 部署全套集群配置（conf-cluster 含 8 项：4 XML + workers + hadoop-env + 环境脚本）
export HADOOP_HOME=/opt/hadoop-3.1.3
bash hadoop/cluster/deploy-cluster-config.sh

# 4. 启动与验证
start-dfs.sh && start-yarn.sh
bash hadoop/cluster/verify-cluster.sh   # 期望 3 DN + 3 NM
```

---

## 配置文件说明

| 目录 | 用途 |
|------|------|
| `conf-pseudo/` | 单机伪分布式（`dfs.replication=1`） |
| `conf-cluster/` | **三节点完整配置**（`dfs.replication=3`，含 core/hdfs/yarn/mapred/workers/hadoop-env.sh） |
| `cluster/` | SSH 免密、配置分发、集群验证脚本 |

### 评分表「8 大配置」对照

| # | 文件 |
|---|------|
| 1 | `core-site.xml` |
| 2 | `hdfs-site.xml` |
| 3 | `yarn-site.xml` |
| 4 | `mapred-site.xml` |
| 5 | `workers` |
| 6 | `hadoop-env.sh` |
| 7 | `/etc/profile.d/hadoop.sh`（安装脚本生成） |
| 8 | SSH 免密（`cluster/setup-ssh-cluster.sh`） |

---

## 常见问题

| 现象 | 处理 |
|------|------|
| `Connection refused 9000` | `start-dfs.sh`；检查 `fs.defaultFS` 与 `/etc/hosts` |
| 扩三节点后只有 1 个 DN | `workers`、SSH 免密、Slave 上 `HADOOP_HOME` 路径一致 |
| 数据目录权限错误 | `sudo chown -R hadoop:hadoop /data/hadoop` |
| 从单机扩容后副本仍为 1 | 新文件自动为 3；旧数据可 `hdfs dfs -setrep -R 3 /Car` |

## 相关文档

- [企业级架构与ETL设计.md](../docs/企业级架构与ETL设计.md)
- [三节点集群部署手册.md](../docs/三节点集群部署手册.md)
- [虚拟机一次性运行手册.md](../docs/虚拟机一次性运行手册.md)
