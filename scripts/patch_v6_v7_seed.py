# -*- coding: utf-8 -*-
"""一次性脚本：将 seed 中 v6/v7 演示数据改为手册对齐后的表结构。"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEED = ROOT / "sql" / "seed" / "charging_bigdata_data.sql"

V6_INSERT = (
    "INSERT INTO `t_voltage_current_relation` "
    "(`id`, `record_hour`, `voltage_change_rate`, `current_change_rate`) VALUES "
    "(1,'00',-0.031,0),(2,'11',0.0309,0),(3,'12',0.0157,0),(4,'13',0.0062,0),(5,'14',0.0031,0);"
)
V7_INSERT = (
    "INSERT INTO `t_soc_temperature` "
    "(`id`, `battery_status`, `avg_max_temperature`, `avg_min_temperature`, "
    "`var_max_temperature`, `var_min_temperature`) VALUES "
    "(1,'idle',32.5,30.8,1.2,0.6),(2,'charging',35.2,33.1,2.4,1.1),(3,'discharging',37.1,35.0,1.8,0.9);"
)


def main() -> None:
    text = SEED.read_text(encoding="utf-8")
    text, n1 = re.subn(
        r"INSERT INTO `t_voltage_current_relation` .*?;",
        V6_INSERT,
        text,
        count=1,
        flags=re.S,
    )
    text, n2 = re.subn(
        r"INSERT INTO `t_soc_temperature` .*?;",
        V7_INSERT,
        text,
        count=1,
        flags=re.S,
    )
    SEED.write_text(text, encoding="utf-8")
    print(f"Patched seed: v6={n1}, v7={n2}")


if __name__ == "__main__":
    main()
