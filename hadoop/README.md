# Hadoop 部署（单机 → 三节点）

本目录提供 **Ubuntu 单机伪分布式** 安装配置，与项目 MapReduce `3.1.3` 版本一致。先单机跑通，再扩展三节点，**无需改 Java 代码**。

## 推荐路线

```text
阶段 1（现在）  单机伪分布式：1 台 Ubuntu 同时担任 NN/DN/RM/NM
阶段 2（答辩前） 三节点集群：Master + 2 Slave，副本数改为 3
```

| 阶段 | 节点 | 角色 |
|------|------|------|
| 单机 | hadoop-master | NameNode + DataNode + ResourceManager + NodeManager |
| 三节点 | hadoop-master | NameNode + ResourceManager + DataNode + NodeManager |
| 三节点 | hadoop-slave1/2 | DataNode + NodeManager |

## 阶段 1：Ubuntu 单机安装

### 1. 把项目拷到 Ubuntu

```bash
# 示例：从 Windows 共享目录或 git 克隆到 Ubuntu
cd ~
# 假设项目在 ~/charging-bigdata
```

### 2. 安装 Hadoop（需 root）

```bash
cd ~/charging-bigdata/hadoop
sudo bash install-pseudo-distributed.sh
```

### 3. 启动集群

```bash
sudo su - hadoop
source /etc/profile.d/hadoop.sh
start-dfs.sh
start-yarn.sh
jps
```

应看到：`NameNode`、`DataNode`、`ResourceManager`、`NodeManager`。

- HDFS Web：`http://hadoop-master:9870` 或 `http://localhost:9870`
- YARN Web：`http://hadoop-master:8088`

### 4. 上传 CSV

把 `F:\项目2资料\数据集\` 四个文件拷到 Ubuntu，例如 `/home/hadoop/dataset/`：

```bash
bash ~/charging-bigdata/hadoop/upload-data.sh /home/hadoop/dataset
```

### 5. 编译并跑 MapReduce

```bash
bash ~/charging-bigdata/hadoop/verify-mr.sh          # 试跑 v1
cd ~/charging-bigdata/mapreduce && bash run-all.sh   # 跑 v1~v7
```

### 6. MySQL 入库（可选，本机装 MySQL）

```bash
mysql -uroot -p < ~/charging-bigdata/sql/schema.sql
cd ~/charging-bigdata/analytics
pip install -r requirements.txt
python scripts/load_mr_to_mysql.py --host 127.0.0.1 --user root --password 你的密码
```

### 7. Windows 上 Python/Web 连 Ubuntu HDFS

在 Windows 后端 `.env` 或环境变量中设置：

```bash
HDFS_NN_HOST=http://<Ubuntu的IP>:9870
HDFS_USER=hadoop
```

---

## 阶段 2：扩展到三节点

> **原则**：Master 主机名保持 `hadoop-master`，避免改项目里所有配置。

### 1. 三台机器统一

- 安装相同版本 JDK8、Hadoop 3.1.3
- `/etc/hosts` 三台互 ping 通（示例）：

```text
192.168.1.101  hadoop-master
192.168.1.102  hadoop-slave1
192.168.1.103  hadoop-slave2
```

- `hadoop` 用户三台 **SSH 免密互访**

### 2. 替换配置

在 **Master** 上：

```bash
cp ~/charging-bigdata/hadoop/conf-cluster/hdfs-site.xml $HADOOP_HOME/etc/hadoop/
cp ~/charging-bigdata/hadoop/conf-cluster/workers $HADOOP_HOME/etc/hadoop/workers
# core-site / yarn-site 与 conf-pseudo 相同，同步到三台
```

将 `conf-pseudo` 下 `core-site.xml`、`mapred-site.xml`、`yarn-site.xml` 复制到三台 `$HADOOP_HOME/etc/hadoop/`。

### 3. 启动顺序

```bash
# 仅在 Master（首次扩集群时若已有数据需谨慎，建议备份）
# 新集群才 format；从单机扩三节点通常不要重新 format
start-dfs.sh
start-yarn.sh
```

在 Slave 上若未自动启动 NM/DN，在 Master 执行：

```bash
hdfs --daemon start datanode   # 一般不用手动
yarn --daemon start nodemanager
```

或 `start-dfs.sh` / `start-yarn.sh` 会按 `workers` 文件 ssh 到各节点启动。

### 4. 验证三节点

```bash
hdfs dfsadmin -report    # 应看到 3 个 Live datanodes
yarn node -list          # 应看到 3 个 NodeManager
```

### 5. 业务侧无需改动

- MR 输入仍为 `/Car/dsv13r1.csv`
- `run-all.sh` 不变
- 副本数从 1 改为 3 后，HDFS 会自动多副本存储

---

## 配置文件说明

| 目录 | 用途 |
|------|------|
| `conf-pseudo/` | 单机伪分布式（副本数 1） |
| `conf-cluster/` | 三节点扩展（workers + 副本数 3） |

## 常见问题

| 现象 | 处理 |
|------|------|
| `Connection refused 9000` | `start-dfs.sh` 未启动或 `fs.defaultFS` 主机名解析错误 |
| MR 报输出目录已存在 | 项目 Job 会自动删输出目录；或 `hdfs dfs -rm -r /Car/output/v1` |
| Windows 访问不了 9870 | Ubuntu 防火墙放行 9870/8088；用虚拟机 IP 而非 localhost |
| 扩三节点后只有 1 个 DN | 检查 `workers`、Slave 上 Hadoop 路径一致、SSH 免密 |

## 相关文档

- [MapReduce统计任务说明.md](../docs/MapReduce统计任务说明.md)
- [需求规格说明书.md](../docs/需求规格说明书.md) §2.3 三节点部署
