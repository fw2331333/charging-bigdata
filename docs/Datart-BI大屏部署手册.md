# Datart BI 大屏部署手册（手册 §5.1–5.3）

本项目 **第五章数据可视化** 采用 **方案一：严格对齐手册**：

| 模块 | 技术 | 说明 |
|------|------|------|
| **BI 大屏** | Datart | Source → View → Chart → Dashboard，效果参考 `visu1.png` |
| **分析页 §5.4** | Vue3 + FastAPI + ECharts | `/bda1`–`/bda5`、预测页 |

数据流不变：

```text
CSV → HDFS → MapReduce v1~v7 → MySQL charging_bigdata → Datart BI + Web API
```

---

## 1. 启动 Datart

### 在 ECS 上用 admin 更新（无需 Windows）

```bash
cd ~/charging-bigdata
git pull origin main

export DATART_PASSWORD='你的admin登录密码'
export MYSQL_PASSWORD='Charging@2026'

bash scripts/setup-datart-bi.sh
```

脚本使用 `http://127.0.0.1:8088`（服务器本机访问 Datart），自动识别 `orgId`，用 **admin** 更新数据源与 v1~v7 视图。若已安装 `pwsh`，会顺带重建 Dashboard 七图。

安装 pwsh（可选，用于自动排版七图）：

```bash
sudo apt update && sudo apt install -y powershell
export DATART_PASSWORD='...'
pwsh scripts/build-datart-dashboard.ps1 -DatartUrl http://127.0.0.1:8088 -DatartUser admin -DatartPassword "$DATART_PASSWORD"
```

---

```powershell
# Windows
powershell -ExecutionPolicy Bypass -File scripts/start-datart.ps1

# Linux / macOS
bash scripts/start-datart.sh
```

浏览器打开：**http://127.0.0.1:8088**  
默认账号：`demo` / `123456`（手册 §5.2）

> 端口 **8088** 是为避免与本项目 Docker Web 默认 **8080** 冲突；手册原命令 `-p 8080:8080` 亦可，需同步修改 `frontend/.env` 中 `VITE_DATART_BASE_URL`。

### 方式 B：与项目 Docker 一并启动

```bash
docker compose -f docker-compose.yml -f docker-compose.datart.yml up -d --build
```

| 地址 | 说明 |
|------|------|
| http://localhost:8080 | Vue Web（§5.4） |
| http://localhost:8088 | Datart BI 大屏 |

首次启动 MySQL 会自动创建 `datart` 应用库（`docker/mysql/04-datart-db.sql`）。若 MySQL 卷已存在，需手动执行：

```sql
CREATE DATABASE IF NOT EXISTS datart DEFAULT CHARSET utf8mb4;
```

---

## 2. 连接业务数据源 charging_bigdata

在 Datart 控制台：**数据源 → 新建 → JDBC / MySQL**

| 项 | 本机 MySQL | Docker Compose |
|----|------------|----------------|
| 主机 | `127.0.0.1` 或 `host.docker.internal` | `mysql`（仅容器内） |
| 端口 | `3306` | `3306` |
| 数据库 | `charging_bigdata` | `charging_bigdata` |
| 用户 | `root` | `root` |
| 密码 | 你的密码（如 `123456`） | `charging123`（见 `.env.docker`） |

验证：能列出表 `t_voltage_current` … `t_soc_temperature`。

---

## 3. 创建 View 与 Chart（v1–v7）

流程：**数据源 → 视图(View) → 图表(Chart) → 可视化(Dashboard)**

下表与 `sql/schema.sql` 一致，布局参考手册 `visu1.png` 七图网格。

| 面板 | MySQL 表 | 时间/维度字段 | 指标字段 | 建议图表 |
|------|----------|---------------|----------|----------|
| v1 组电压与充电电流 | `t_voltage_current` | `record_hour` | `avg_pack_voltage`, `avg_charge_current` | 双轴折线 |
| v2 单体电压范围 | `t_cell_voltage_range` | `record_hour` | `max_cell_voltage`, `min_cell_voltage` | 双折线 |
| v3 电池温度趋势 | `t_temperature` | `record_time` | `max_temperature`, `min_temperature` | 双折线 |
| v4 可用能量与容量 | `t_energy_capacity` | `record_hour` | `avg_available_energy`, `avg_available_capacity` | 双轴折线 |
| v5 充电电流统计 | `t_charge_current_stats` | `record_hour` | `avg_charge_current`, `max_charge_current` | 双折线 |
| v6 组电压变化率 | `t_voltage_current_relation` | `record_hour` | `voltage_change_rate`, `current_change_rate` | 双折线（小时内平均变化率；电流按 \|I\|） |
| v7 电池状态温度 | `t_soc_temperature` | `battery_status` | `avg_max/min_temperature`, `var_max/min_temperature` | 双轴（左均值、右方差） |

也可直接使用已有 SQL 视图：`v_voltage_current`、`v_temperature`、`v_soc_temperature`。

**时间轴格式化**：`record_hour` / `record_time` 为 `yyyyMMddHH` 或 `yyyyMMddHHmmss` 字符串，在 View 中可按需 `SUBSTRING` 或 Datart 格式化函数展示为可读时间。

---

## 4. 组装 Dashboard 并分享

1. **可视化 → 新建仪表板**，拖入上述 7 个 Chart，排版对齐 `visu1.png`。
2. 标题建议：**东软电力新能源充电电池桩大数据可视化**。
3. **分享 → 公开链接**，复制 URL，形如：

```text
http://127.0.0.1:8088/shareDashboard/xxxxxxxxxxxxxxxx?type=NONE
```

4. 写入前端环境变量（`frontend/.env` 或 Docker build arg）：

```env
VITE_DATART_BASE_URL=http://127.0.0.1:8088
VITE_DATART_DASHBOARD_URL=http://127.0.0.1:8088/shareDashboard/你的token?type=NONE
```

重启前端 `npm run dev` 后，首页 **「Datart BI 大屏」** 按钮将直接打开分享页。

---

## 5. Vue Web 入口说明

| 入口 | 行为 |
|------|------|
| 首页按钮 | 新窗口打开 `VITE_DATART_DASHBOARD_URL`（未配置则打开 Datart 首页） |
| 侧栏 | **不含** BI 项（与手册 Flask 侧栏一致） |

---

## 6. 与 Vue Web 的关系

- **答辩/验收主线**：Datart Dashboard（手册 §5.1–5.3）。
- **Vue Web**：§5.4 自定义分析页与预测页；BI 大屏不在应用内嵌 ECharts 实现。
- **不包含**：多租户管理、应用内数据源 CRUD、定时推送（非手册要求）。

---

## 7. 故障排查

| 现象 | 处理 |
|------|------|
| 8088 无法访问 | `docker ps` 确认 `cbp-datart` 运行；`docker logs cbp-datart` |
| Datart 连不上 MySQL | Windows Docker 访问本机库用 `host.docker.internal`；Compose 内用服务名 `mysql` |
| 图表无数据 | 先执行 `scripts/import_web_demo.ps1` 导入种子；`SELECT COUNT(*) FROM t_voltage_current` |
| 分享链接 404 | Dashboard 需发布并开启分享；检查 `VITE_DATART_DASHBOARD_URL` 是否完整 |
| **一直 Loading / 空白** | 见下方「Loading 专项」 |
| 端口与手册不一致 | 手册为 `8080:8080`；本项目 Web 已占 8080 时 Datart 用 **8088** 即可 |

### Loading 专项（Datart 1.0.0-rc.3）

根因通常是 **API 写入的 JSON 与 Datart 前端迁移版本不兼容**：

1. **仪表板 `config` JSON 损坏**（含中文 i18n 经 API 保存后乱码）→ 前端 `JSON.parse` 失败，永远 Loading  
   - 修复：重跑 `scripts/build-datart-dashboard.ps1`（仅 ASCII `i18ns:[]`）
2. **图表 config 缺 `chartConfig` 包装** → `ChartDataRequestBuilder` 读不到 `datas`  
   - 修复：脚本已改为 `{ aggregation, chartGraphId, chartConfig: { datas, ... } }`
3. **Widget `version: 3.0`** 不在 Datart 语义版本表内 → 跳过 beta4 迁移，`customConfig` 为空  
   - 修复：脚本使用 `1.0.0-beta.0` + `content.type: dataChart`
4. **登录态失效**（JWT NPE / 401）→ 阅读页拿不到 `/viz/dashboards/{id}`  
   - 处理：Datart 内 **切换账号** 重新登录 `demo / 123456`，或清除 `127.0.0.1:8088` 站点数据后重登

一键修复命令：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/fix-datart-view-models.ps1
powershell -ExecutionPolicy Bypass -File scripts/build-datart-dashboard.ps1
```

验收：登录后打开 `Charging-BigData-BI`，或分享页  
`http://127.0.0.1:8088/shareDashboard/ee67d4cb16654f9a8d59cc61630b23c2?type=NONE`  
应出现 7 个图表格子。若仍异常，可先用 Vue 大屏 `http://127.0.0.1:5173/mr-bi` 展示数据。

---

## 8. 参考

- 项目手册：第五章 数据可视化
- Datart 文档：<http://running-elephant.gitee.io/datart-docs/docs/index.html>
- 效果图：`visu1.png`（手册 assets）
