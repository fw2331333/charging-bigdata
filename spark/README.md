# Spark SQL（ADS 汇总层）



| ADS 表 | 数据源 | 指导书 |

|--------|--------|--------|

| `t_soc_hourly` / `t_soc_heatmap` / `t_charge_rate_hourly` | **dsv13r2** §3.2 | §9.2 任务二~五 |

| `t_charging_daily` / `t_charging_monthly` | **nvv2t** `created` §3.3 | §9.2 任务一 |

| ML 预测 | **nvv2t_md** §3.4 | §10 |



`created` 字段 `0014-xx` → `2014-xx`（与 `nvv2t_md` 同会话一致）。



虚拟机操作见 [docs/虚拟机一次性运行手册.md](../docs/虚拟机一次性运行手册.md)。



```bash

cd /media/sf_cs-/charging-bigdata

bash scripts/run-pipeline.sh

```

