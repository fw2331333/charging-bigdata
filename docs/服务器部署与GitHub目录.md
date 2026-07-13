# 服务器部署与 GitHub 上传目录说明

> 适用：**Ubuntu 22.04 云服务器 + Docker 一键部署 Web 演示**（推荐）。  
> 完整 Hadoop 三节点见 [三节点集群部署手册.md](./三节点集群部署手册.md)。

---

## 1. 部署方式选择

| 方式 | 需要上传 GitHub 的范围 | 服务器需要安装 |
|------|------------------------|----------------|
| **Docker 一键（推荐）** | 见下文「必传目录」 | Docker + Compose v2 |
| 手动安装 | 同上 + 在服务器 `npm ci` / `pip install` | MySQL 8、Python 3.10+、Node 20+ |
| 完整大数据 | 整个仓库（含 hadoop/spark/mapreduce） | JDK 8、Hadoop 3.1.3 等 |

答辩 / 生产演示 Web：**只需 Docker 方式 + 必传目录**。

---

## 2. 必传 GitHub 目录（服务器 `git clone` 后可直接 `docker compose up`）

```
charging-bigdata/
├── docker-compose.yml              # 主栈：MySQL + backend + frontend
├── docker-compose.datart.yml       # 可选：叠加 Datart BI
├── .env.docker.example             # 复制为 .env.docker 后改密码/域名
│
├── docker/
│   ├── README.md
│   ├── mysql/03-seed.sh            # 首次导入 BI 种子数据
│   ├── mysql/04-datart-db.sql      # 仅 Datart 叠加时需要
│   └── datart/*.conf               # 仅 Datart 叠加时需要
│
├── sql/
│   ├── schema.sql                  # MR 业务表
│   ├── ads_schema.sql              # ADS 分析表
│   ├── auth_schema.sql             # 用户 / Refresh Token
│   ├── view_config_schema.sql      # BI 下钻配置
│   ├── migrations/                 # 邮箱注册等增量（Docker 会自动执行 004/005）
│   └── seed/
│       ├── charging_bigdata_data.sql   # 图表数据（必传，体积较大）
│       └── auth_users.sql              # 演示账号 admin / user
│
├── backend/
│   ├── Dockerfile
│   ├── main.py
│   ├── requirements.txt
│   ├── .env.example                # 手动部署时复制为 .env（勿提交 .env）
│   └── app/                        # 整个后端源码目录
│
├── frontend/
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── package.json
│   ├── package-lock.json
│   ├── .env.example
│   ├── index.html
│   ├── vite.config.ts
│   ├── tsconfig*.json
│   ├── public/
│   └── src/                        # 整个前端源码目录
│
├── analytics/
│   ├── output/models/.gitkeep
│   ├── output/models/metrics.json          # 建议提交（bda5 / 指标页）
│   ├── output/models/performance_report.json
│   └── output/models/*.pkl                 # 可选：预测页需要（约 3MB，可提交或 Release 下载）
│
└── README.md
```

上传前在本机执行校验：

```bash
# Linux / macOS / 服务器
bash scripts/check-deploy-files.sh

# Windows
powershell -ExecutionPolicy Bypass -File scripts/check-deploy-files.ps1
```

---

## 3. 建议提交（功能完整，非 Docker 构建必需）

```
analytics/                    # 训练脚本（服务器上重训模型时用）
├── battery_performance.py
├── ml_data.py
├── ml_train_utils.py
└── scripts/
    ├── train_all_models.py
    └── ds_battery7_1.py

docs/                         # 部署与答辩文档
scripts/
├── import_web_demo.ps1
├── import_web_demo.sh
├── start-datart.ps1
└── start-datart.sh

frontend/src/locales/         # 中英文
sql/migrations/002_*.sql      # 旧库升级用（新 Docker 可不跑）
sql/migrations/003_*.sql
```

---

## 4. 可选提交（大数据全链路 / Datart，Web 演示可不传）

```
hadoop/
mapreduce/
spark/
hive/
analytics/etl/
config/pipeline.env.example
scripts/run-pipeline.sh
scripts/build-datart-dashboard.ps1
scripts/datart-export.*
```

---

## 5. 禁止提交 Git（已在 .gitignore）

| 类型 | 示例 |
|------|------|
| 密钥 / 环境 | `.env`、`backend/.env`、`config/pipeline.env` |
| 依赖 / 构建产物 | `node_modules/`、`frontend/dist/`、`backend/.venv/` |
| 原始数据集 | `*.csv`、`data/`、`datasets/` |
| 本地缓存 | `backend/chroma_db/`、`logs/` |

SMTP 授权码、DeepSeek API Key、JWT 密钥：**只在服务器 `.env.docker` 或 `backend/.env` 配置，不要 push**。

---

## 6. 服务器部署步骤（Docker）

```bash
# 1. 安装 Docker（Ubuntu 22.04）
sudo apt update && sudo apt install -y docker.io docker-compose-v2
sudo systemctl enable --now docker

# 2. 拉代码
git clone https://github.com/<你的用户名>/charging-bigdata.git
cd charging-bigdata

# 3. 配置（必改项见 .env.docker.example 注释）
cp .env.docker.example .env.docker
nano .env.docker

# 4. 构建并启动
docker compose --env-file .env.docker up -d --build

# 5. 云安全组放行 TCP：8080（Web），可选 8088（Datart）
```

浏览器访问：`http://<公网IP>:8080`  
演示登录：`admin@example.com` / `admin123`

### `.env.docker` 生产必改示例

```env
MYSQL_ROOT_PASSWORD=强密码
WEB_PORT=8080
PUBLIC_HOST=http://你的公网IP:8080
CORS_ORIGINS=http://你的公网IP:8080
APP_PUBLIC_URL=http://你的公网IP:8080
JWT_SECRET=随机长字符串

# 邮箱注册（可选）
SMTP_HOST=smtp.qq.com
SMTP_PORT=587
SMTP_USER=你的邮箱
SMTP_PASSWORD=授权码
SMTP_FROM=充电大数据平台 <你的邮箱>
SMTP_USE_TLS=true
```

修改 `.env.docker` 后执行：`docker compose --env-file .env.docker up -d --build`

### 含 Datart BI

```bash
docker compose -f docker-compose.yml -f docker-compose.datart.yml --env-file .env.docker up -d --build
```

---

## 7. 首次 push 到 GitHub 建议命令

在项目根目录（**确认无 .env / csv 被加入**）：

```bash
git add docker-compose.yml docker-compose.datart.yml .env.docker.example .gitignore
git add docker/ sql/ backend/ frontend/ analytics/output/models/
git add docs/ scripts/check-deploy-files.sh scripts/check-deploy-files.ps1
git add README.md docs/服务器部署与GitHub目录.md

git status   # 检查：不应出现 .env、*.csv、node_modules

git commit -m "chore: prepare server deploy bundle"
git push origin main
```

若预测页要开箱即用，额外添加模型：

```bash
git add analytics/output/models/*.pkl analytics/output/models/*.json
```

---

## 8. 常见问题

| 现象 | 处理 |
|------|------|
| `registry-1.docker.io` **i/o timeout** | 国内 ECS 常见，见下文「Docker 镜像加速」 |
| 图表空白 | `docker compose down -v` 后重新 `up`（重建库） |
| 注册 500 | 确认 `sql/migrations/004` 已在 Docker 初始化中执行 |
| 预测页报错 | 上传 `analytics/output/models/*.pkl` 或服务器训练后挂载 |
| 邮件发不出 | 检查 `.env.docker` SMTP；`APP_PUBLIC_URL` 改为公网地址 |
| CORS 错误 | `CORS_ORIGINS` 与浏览器访问地址完全一致 |

### Docker 镜像加速（阿里云 ECS 拉取 mysql 超时）

```bash
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json <<'EOF'
{
  "registry-mirrors": [
    "https://docker.1ms.run",
    "https://docker.xuanyuan.me"
  ]
}
EOF
sudo systemctl daemon-reload
sudo systemctl restart docker
docker pull mysql:8.0
```

若仍失败：登录 [阿里云控制台](https://cr.console.aliyun.com) → **容器镜像服务** → **镜像工具** → **镜像加速器**，把专属地址 `https://xxxx.mirror.aliyuncs.com` 放进 `registry-mirrors` 第一项后重启 Docker。

```bash
cd ~/charging-bigdata
docker compose --env-file .env.docker up -d --build
```
