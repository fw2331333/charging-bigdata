# Docker 一键启动（无需本机安装 MySQL / Node / Python）

适合在别人电脑上**最快跑通 Web 图表**（数据已内置在 `sql/seed/`）。

## 环境要求

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)（Windows / macOS）
- 或 Linux 已安装 Docker Engine + Compose v2

## 一键启动

```bash
git clone https://github.com/fw2331333/charging-bigdata.git
cd charging-bigdata

# 可选：复制并修改 root 密码、Web 端口
copy .env.docker.example .env.docker    # Linux: cp .env.docker.example .env.docker

docker compose --env-file .env.docker.example up -d --build
```

首次构建约 3～8 分钟；MySQL 首次启动会自动导入：

1. `sql/schema.sql`
2. `sql/ads_schema.sql`
3. `sql/seed/charging_bigdata_data.sql`

## 访问

| 地址 | 说明 |
|------|------|
| http://localhost:8080 | 前端页面（默认端口） |
| http://localhost:8000/docs | 仅当映射 backend 端口时可用（默认未映射） |

## 常用命令

```bash
# 查看状态
docker compose ps

# 查看日志
docker compose logs -f backend

# 停止
docker compose down

# 停止并清空数据库卷（下次会重新导入 SQL）
docker compose down -v
```

## 预测页（可选）

容器会只读挂载 `analytics/output/models/`。若目录里没有 `.pkl`，图表正常、预测页报错。

在本机训练后复制模型进仓库目录再重建：

```bash
# Windows 训练后
dir analytics\output\models\*.pkl

docker compose up -d --build backend
```

或从 GitHub Releases 下载 `web-demo-bundle.zip`，解压 `models/` 到 `analytics/output/models/`。

## 自定义密码

编辑 `.env.docker`：

```env
MYSQL_ROOT_PASSWORD=你的强密码
WEB_PORT=8080
```

```bash
docker compose --env-file .env.docker up -d --build
```

## 与手动安装对比

| 方式 | 需要安装 | 适用 |
|------|----------|------|
| **Docker** | 仅 Docker | 别人电脑快速演示 |
| `import_web_demo.ps1` | MySQL + Python + Node | 本机开发调试 |
| 虚拟机流水线 | Hadoop + Spark | 完整大数据链路 |

## 故障排查

| 现象 | 处理 |
|------|------|
| 前端 502 | `docker compose logs backend`，等 MySQL healthy |
| 图表空白 | `docker compose down -v` 后重新 `up`（重建库） |
| 端口占用 | 改 `.env.docker` 里 `WEB_PORT=8888` |
| Windows 路径错误 | 在项目根目录执行 compose，路径含中文一般可用 |
