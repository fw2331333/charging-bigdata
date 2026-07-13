# -*- coding: utf-8 -*-
"""机器学习数据读取与特征工程（nvv2t_md / dsv13r2）。"""
from __future__ import annotations

import csv
import io
from datetime import datetime
from pathlib import Path
from typing import Iterator

from analytics.hdfs_io import read_lines

WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
NVV2T_HEADER = [
    "sessionId", "kwhTotal", "charging_fees", "created", "ended", "startTime", "endTime",
    "chargeTimeHrs", "weekday", "platform", "userId", "stationId", "locationId",
    "managerVehicle", "facilityType", "Mon", "Tues", "Wed", "Thurs", "Fri", "Sat", "Sun",
]


def iter_lines(hdfs_path: str | None = None, local_path: str | None = None) -> Iterator[str]:
    if local_path:
        p = Path(local_path)
        with p.open("r", encoding="utf-8-sig") as f:
            for line in f:
                yield line.rstrip("\n")
    elif hdfs_path:
        yield from read_lines(hdfs_path)
    else:
        raise ValueError("须指定 hdfs_path 或 local_path")


def weekday_code(wd: str) -> float:
    wd = (wd or "").strip()[:3].title()
    mapping = {"Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3, "Fri": 4, "Sat": 5, "Sun": 6}
    return float(mapping.get(wd, 0))


def platform_code(p: str) -> float:
    return 1.0 if (p or "").lower() == "android" else 0.0


def weekday_label(dt: datetime) -> str:
    return WEEKDAYS[dt.weekday()]


def charge_hours_between(start_at: datetime, end_at: datetime) -> float:
    return (end_at - start_at).total_seconds() / 3600.0


def session_row_from_datetimes(
    start_at: datetime,
    end_at: datetime,
    *,
    kwh_total: float,
    weekday: str | None = None,
    platform: str = "android",
    facility_type: int = 0,
    station_id: int = 0,
    charge_time_hrs: float | None = None,
    charging_fees: float | None = None,
) -> dict[str, str]:
    """将起止日期时间转为与 nvv2t_md 一致的特征行（支持跨日，endTime 可为次日小时）。"""
    hrs = charge_time_hrs if charge_time_hrs is not None else charge_hours_between(start_at, end_at)
    row: dict[str, str] = {
        "kwhTotal": str(kwh_total),
        "startTime": str(start_at.hour),
        "endTime": str(end_at.hour),
        "chargeTimeHrs": str(hrs),
        "weekday": weekday or weekday_label(start_at),
        "platform": platform,
        "facilityType": str(facility_type),
        "stationId": str(station_id),
    }
    if charging_fees is not None:
        row["charging_fees"] = str(charging_fees)
    return row


def parse_nvv2t_rows(
    hdfs_path: str | None = None,
    local_path: str | None = None,
    max_rows: int = 80000,
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    it = iter_lines(hdfs_path, local_path)
    first = next(it, "")
    if not first:
        return rows
    # 有表头
    if first.lower().startswith("sessionid"):
        header = [h.strip() for h in first.split(",")]
    else:
        header = NVV2T_HEADER
        rows.append(dict(zip(header, first.split(","))))

    for i, line in enumerate(it):
        if len(rows) >= max_rows:
            break
        if not line.strip():
            continue
        parts = line.split(",")
        if len(parts) < 10:
            continue
        row = dict(zip(header, parts))
        rows.append(row)
    return rows


def session_features(row: dict[str, str]) -> list[float] | None:
    try:
        return [
            float(row["kwhTotal"]),
            float(row["startTime"]),
            float(row["endTime"]),
            float(row["chargeTimeHrs"]),
            weekday_code(row.get("weekday", "Mon")),
            platform_code(row.get("platform", "android")),
            float(row.get("facilityType", 0)),
            float(row.get("stationId", 0)) % 10000,
        ]
    except (KeyError, ValueError):
        return None


def fee_feature_names() -> list[str]:
    return ["kwhTotal", "startTime", "endTime", "chargeTimeHrs", "weekday", "platform", "facilityType", "stationId"]


def duration_feature_names() -> list[str]:
    return ["kwhTotal", "startTime", "endTime", "weekday", "platform", "facilityType", "stationId"]


def platform_feature_names() -> list[str]:
    return ["kwhTotal", "charging_fees", "chargeTimeHrs", "startTime", "weekday", "facilityType"]


def duration_features(row: dict[str, str]) -> list[float] | None:
    try:
        return [
            float(row["kwhTotal"]),
            float(row["startTime"]),
            float(row["endTime"]),
            weekday_code(row.get("weekday", "Mon")),
            platform_code(row.get("platform", "android")),
            float(row.get("facilityType", 0)),
            float(row.get("stationId", 0)) % 10000,
        ]
    except (KeyError, ValueError):
        return None


def platform_features(row: dict[str, str]) -> list[float] | None:
    try:
        return [
            float(row["kwhTotal"]),
            float(row["charging_fees"]),
            float(row["chargeTimeHrs"]),
            float(row["startTime"]),
            weekday_code(row.get("weekday", "Mon")),
            float(row.get("facilityType", 0)),
        ]
    except (KeyError, ValueError):
        return None


def parse_dsv13r2_rows(
    hdfs_path: str | None = None,
    local_path: str | None = None,
    max_rows: int = 80000,
) -> list[dict[str, float]]:
    """解析 dsv13r2，返回数值行（用于 SOC 预测训练）。"""
    out: list[dict[str, float]] = []
    it = iter_lines(hdfs_path, local_path)
    header_line = next(it, "")
    if not header_line:
        return out
    # skip header
    for line in it:
        if len(out) >= max_rows:
            break
        if not line.strip():
            continue
        parts = line.split(",")
        if len(parts) < 11:
            continue
        try:
            row = {
                "soc": float(parts[2]),
                "pack_voltage": float(parts[3]),
                "charge_current": float(parts[4]),
                "max_cell_v": float(parts[5]),
                "min_cell_v": float(parts[6]),
                "max_temp": float(parts[7]),
                "min_temp": float(parts[8]),
                "energy": float(parts[9]),
                "capacity": float(parts[10]),
            }
        except ValueError:
            continue
        # 丢弃物理上不合理的边界（最低高于最高）
        if row["min_cell_v"] > row["max_cell_v"]:
            continue
        if row["min_temp"] > row["max_temp"]:
            continue
        out.append(row)
    return out


def soc_features(row: dict[str, float]) -> list[float]:
    return [
        row["pack_voltage"],
        row["charge_current"],
        row["max_cell_v"],
        row["min_cell_v"],
        row["max_temp"],
        row["min_temp"],
        row["energy"],
        row["capacity"],
    ]


def soc_feature_names() -> list[str]:
    return [
        "pack_voltage", "charge_current", "max_cell_v", "min_cell_v",
        "max_temp", "min_temp", "energy", "capacity",
    ]
