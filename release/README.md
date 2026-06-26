# 发布包说明

## 仓库内已包含

- `sql/seed/charging_bigdata_data.sql` — 图表用 MySQL 数据（约 100KB，随 Git 提交）

## 可选 Release 附件（体积较大）

预测页需要 `.pkl` 模型（约 45MB），默认 **不提交 Git**。维护者可执行：

```powershell
powershell -File scripts/package_web_demo.ps1
```

生成 `release/web-demo-bundle.zip`，内含：

- `schema.sql`、`ads_schema.sql`、`charging_bigdata_data.sql`
- `models/*.pkl`、`metrics.json`

他人下载解压后：

```text
sql/*.sql          → 按 import_web_demo 脚本导入
models/            → 复制到 analytics/output/models/
```

若不使用预测页，仅导入 SQL 即可浏览全部图表。
