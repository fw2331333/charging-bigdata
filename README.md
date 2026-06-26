# 新能源充电桩大数据分析项目

> Web 演示：**无需 Hadoop**，导入仓库内 MySQL 种子数据即可跑通全部图表页。  
> 完整大数据链路（HDFS + MapReduce + Spark）见 [docs/虚拟机一次性运行手册.md](docs/虚拟机一次性运行手册.md)。

## 环境要求

| 组件 | 版本建议 |
|------|----------|
| Python | 3.10+ |
| Node.js | 18+ |
| MySQL | 8.0+ |

## 他人快速开始（仅 Web，推荐）

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
| MR 汇总 BI | MySQL MR 表（已导入） |
| SOC / 充电 / 速率 / 热力图 | MySQL ADS 表（已导入） |
| 四项预测 | 需额外准备模型，见下文 |

### 5. 预测页（可选）

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
├── backend/           # FastAPI（读 MySQL + 加载模型）
├── frontend/          # Vue3 + ECharts
├── sql/
│   ├── schema.sql     # MR 表结构
│   ├── ads_schema.sql # ADS 表结构
│   └── seed/          # 预置数据（Web 演示）
├── analytics/         # ML 训练脚本
├── mapreduce/         # Hadoop MR（完整链路用）
├── spark/             # Spark ADS（完整链路用）
├── scripts/
│   ├── import_web_demo.ps1   # 一键导入 MySQL
│   └── run-pipeline.sh       # 虚拟机全量流水线
└── docs/
```

## 数据流说明

### Web 演示模式（本 README 主线）

```text
sql/seed/charging_bigdata_data.sql
        ↓ 导入
     MySQL
        ↓ 只读
  FastAPI /api/v1/bi/*
        ↓
  Vue + ECharts 图表页
```

### 完整大数据模式（可选）

```text
HDFS /Car/（四个 CSV）
    ├─→ dsv13r1 → MapReduce v1~v7 → MySQL MR 表
    ├─→ dsv13r2 → Spark ADS → SOC / 速率 / 热力图
    ├─→ nvv2t   → Spark ADS → 日/月充电次数
    └─→ nvv2t_md → Python ML → 预测模型
```

详见 [docs/虚拟机一次性运行手册.md](docs/虚拟机一次性运行手册.md)。

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
| [sql/seed/README.md](sql/seed/README.md) | 种子数据说明 |
| [release/README.md](release/README.md) | Release 包说明 |
| [docs/MySQL远程配置与建库.md](docs/MySQL远程配置与建库.md) | MySQL 详细配置 |
| [docs/虚拟机一次性运行手册.md](docs/虚拟机一次性运行手册.md) | Hadoop 全链路 |

## 安全提示

- **勿提交** `backend/.env`、`config/pipeline.env`（已在 `.gitignore`）
- 种子数据为实训汇总结果，不含原始 CSV
- 公开仓库请使用强密码，勿使用 `123456`
