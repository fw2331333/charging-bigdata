# 新能源充电桩大数据分析项目

> **企业级分层**：HDFS 计算 → 独立 ETL 入 MySQL 服务层 → FastAPI → Vue。  
> MR **不直连 MySQL**（ETL 幂等写入），详见 [docs/企业级架构与ETL设计.md](docs/企业级架构与ETL设计.md)。  
> Web 演示：**无需 Hadoop**，导入种子 SQL 即可。三节点部署见 [docs/三节点集群部署手册.md](docs/三节点集群部署手册.md)。

## 环境要求

| 组件 | 版本建议 |
|------|----------|
| Python | 3.10+ |
| Node.js | 18+ |
| MySQL | 8.0+（手动安装方式需要） |
| Docker | 20+（**一键方式**，见下） |

## Docker 一键启动（别人电脑 / 云服务器最快）

无需本机 MySQL / Python / Node，自动导入 SQL 种子。详见 [docker/README.md](docker/README.md)。

**上传 GitHub 与云服务器部署目录说明**：[docs/服务器部署与GitHub目录.md](docs/服务器部署与GitHub目录.md)

上传前可校验：`powershell -File scripts/check-deploy-files.ps1` 或 `bash scripts/check-deploy-files.sh`

```bash
git clone https://github.com/fw2331333/charging-bigdata.git
cd charging-bigdata
cp .env.docker.example .env.docker   # 改公网 IP、密码、JWT、SMTP
docker compose --env-file .env.docker up -d --build
```

浏览器打开：**http://localhost:8080**（服务器改为公网 IP + 安全组放行 8080）

---

## 他人快速开始（手动安装 MySQL）

适合：只想本地看 **MR BI / SOC / 充电 / 热力图 / 速率** 等页面，不装 Hadoop。

### 1. 克隆仓库

```bash
git clone https://github.com/<你的用户名>/charging-bigdata.git
cd charging-bigdata
```

### 2. 导入预置 MySQL 数据

仓库已包含处理好的汇总数据：`sql/seed/charging_bigdata_data.sql`（MR + ADS 全表）。

**Windows（PowerShell）：**

```powershell
# 若 mysql 不在 PATH，可加参数 -Mysql "E:\mysql-8.4.8-winx64\bin\mysql.exe"
powershell -ExecutionPolicy Bypass -File scripts/import_web_demo.ps1 -Password your_password
```

**Linux / macOS：**

```bash
MYSQL_PASSWORD=your_password bash scripts/import_web_demo.sh
```

**手动导入（等价）：**

```bash
mysql -uroot -p < sql/schema.sql
mysql -uroot -p < sql/ads_schema.sql
mysql -uroot -p charging_bigdata < sql/seed/charging_bigdata_data.sql
```

验证：

```bash
mysql -uroot -p charging_bigdata -e "SELECT COUNT(*) FROM t_soc_hourly; SELECT COUNT(*) FROM t_voltage_current;"
```

### 3. 配置后端

```powershell
cd backend
copy .env.example .env    # Linux: cp .env.example .env
```

编辑 `backend/.env`，至少修改：

```env
MYSQL_PASSWORD=your_password
```

### 4. 安装依赖并启动

```powershell
# 后端
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000

# 新终端 — 前端
cd frontend
npm install
npm run dev
```

浏览器打开：**http://127.0.0.1:5173**

| 页面 | 数据来源 |
|------|----------|
| **Datart BI 大屏**（手册 §5.1–5.3） | MySQL `charging_bigdata` MR 表，在 Datart 中配置 |
| SOC / 充电 / 速率 / 热力图（§5.4） | MySQL ADS 表（已导入） |
| 四项预测 | 需额外准备模型，见下文 |

### 5. Datart BI 大屏（手册第五章主入口）

```powershell
# 启动 Datart（映射本机 8088，避免与 Docker Web 8080 冲突）
powershell -ExecutionPolicy Bypass -File scripts/start-datart.ps1

# 可选：复制前端环境变量
cd frontend
copy .env.example .env
```

1. 浏览器打开 **http://127.0.0.1:8088**，登录 `demo` / `123456`
2. 在 Datart 中连接 MySQL 库 `charging_bigdata`，按 v1–v7 建 View / Chart / Dashboard
3. 分享 Dashboard 后，将链接写入 `frontend/.env` 的 `VITE_DATART_DASHBOARD_URL`
4. Vue 首页 **「Datart BI 大屏」** 按钮将新窗口打开 Datart

完整步骤见 **[docs/Datart-BI大屏部署手册.md](docs/Datart-BI大屏部署手册.md)**。

Docker 一并启动 Datart：

```bash
docker compose -f docker-compose.yml -f docker-compose.datart.yml up -d --build
```

### 6. 预测页（可选）

图表不依赖 Hadoop；**预测接口**需要 `analytics/output/models/*.pkl`。

**方式 A — 下载 Release 包（推荐）**

维护者在 [Releases](https://github.com/<你的用户名>/charging-bigdata/releases) 上传 `web-demo-bundle.zip` 后，解压并将 `models/` 复制到：

```text
charging-bigdata/analytics/output/models/
```

**方式 B — 自行训练（需课程 CSV）**

```powershell
pip install -r analytics/requirements.txt
python analytics/scripts/train_all_models.py ^
  --local-nvv path\to\nvv2t_md.csv ^
  --local-dsv path\to\dsv13r2.csv
```

---

## 目录结构

```text
charging-bigdata/
├── backend/              # FastAPI 服务层（api → service → repository）
│   └── app/
│       ├── api/v1/       # REST 路由
│       ├── services/     # 业务编排
│       ├── repositories/ # MySQL 只读访问
│       ├── schemas/      # 响应模型
│       └── core/         # 配置、连接池、常量
├── frontend/             # Vue3 + ECharts 展示层
├── analytics/
│   ├── etl/              # MR → MySQL 企业级 ETL 包
│   └── scripts/          # ETL CLI、ML 训练
├── mapreduce/            # Hadoop MR v1~v7（只写 HDFS）
├── spark/                # Spark ADS → MySQL
├── hadoop/
│   ├── conf-pseudo/      # 单机配置
│   ├── conf-cluster/     # 三节点完整配置
│   └── cluster/          # SSH 免密、部署、验证脚本
├── sql/                  # schema + seed
├── scripts/              # run-pipeline.sh 单入口流水线
└── docs/
```

## 数据流说明

### 企业级离线链路（推荐答辩主线）

```text
HDFS /Car/*.csv
    ├─→ MapReduce v1~v7 ──→ HDFS /Car/output/v*
    │                              ↓
    │                    analytics/etl（幂等 UPSERT）
    │                              ↓
    ├─→ Spark ADS ─────────────→ MySQL 服务层
    └─→ Python ML ──→ .pkl
                              ↓
                    FastAPI /api/v1/*
                              ↓
                    Vue + ECharts
```

### Web 演示模式（无 Hadoop）

```text
sql/seed/charging_bigdata_data.sql
        ↓ 导入
     MySQL charging_bigdata
        ├─→ Datart BI 大屏（手册 §5.1–5.3）
        └─→ FastAPI /api/v1/* → Vue ECharts 分析页（§5.4）
```

### 完整大数据模式（三节点 + ETL）

```text
HDFS /Car/（四个 CSV，副本数 3）
    ├─→ dsv13r1 → MapReduce v1~v7 → HDFS 结果
    │                    ↓ ETL（非 Reducer JDBC）
    │                 MySQL MR 表
    ├─→ dsv13r2 + nvv2t → Spark ADS → MySQL ADS 表
    └─→ nvv2t_md → Python ML → 预测模型
```

详见 [docs/虚拟机一次性运行手册.md](docs/虚拟机一次性运行手册.md)、[docs/三节点集群部署手册.md](docs/三节点集群部署手册.md)。

## 维护者：更新种子数据

本机跑完虚拟机流水线后，在 Windows 执行：

```powershell
powershell -File scripts/export_mysql_seed.ps1
git add sql/seed/charging_bigdata_data.sql
```

打包 Release（含模型）：

```powershell
powershell -File scripts/package_web_demo.ps1
# 上传 release/web-demo-bundle.zip 到 GitHub Releases
```

## 文档

| 文档 | 说明 |
|------|------|
| [docs/Datart-BI大屏部署手册.md](docs/Datart-BI大屏部署手册.md) | **手册 §5.1–5.3** Datart 部署、数据源、七图 Dashboard |
| [docs/企业级架构与ETL设计.md](docs/企业级架构与ETL设计.md) | 分层架构、ETL 选型、评分对照 |
| [docs/三节点集群部署手册.md](docs/三节点集群部署手册.md) | 真三节点 SSH/Hadoop 部署 |
| [sql/seed/README.md](sql/seed/README.md) | 种子数据说明 |
| [release/README.md](release/README.md) | Release 包说明 |
| [docs/MySQL远程配置与建库.md](docs/MySQL远程配置与建库.md) | MySQL 详细配置 |
| [docs/虚拟机一次性运行手册.md](docs/虚拟机一次性运行手册.md) | 虚拟机全链路 |
| [hadoop/README.md](hadoop/README.md) | Hadoop 配置与集群脚本 |

## 安全提示

- **勿提交** `backend/.env`、`config/pipeline.env`（已在 `.gitignore`）
- 种子数据为实训汇总结果，不含原始 CSV
- 公开仓库请使用强密码，勿使用 `123456`
