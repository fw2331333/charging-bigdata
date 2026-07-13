#!/usr/bin/env python3
"""一键修复 Datart：数据源 + 视图 + 七图（RC.3 完整 styles）+ Dashboard。"""
from __future__ import annotations

import json
import os
import sys
import uuid
import urllib.error
import urllib.request
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from datart_rc3_builders import (  # noqa: E402
    AUTO_BOARD,
    CHART_BUILDERS,
    load_widget_custom,
)

BASE = os.environ.get("DATART_URL", "http://127.0.0.1:8088").rstrip("/")
USER = os.environ.get("DATART_USER", "admin")
PASS = os.environ.get("DATART_PASSWORD", "123456")
MYSQL_HOST = os.environ.get("MYSQL_HOST", "mysql")
MYSQL_PW = os.environ.get("MYSQL_PASSWORD", "Charging@2026")
JDBC = (
    f"jdbc:mysql://{MYSQL_HOST}:3306/charging_bigdata"
    "?useUnicode=true&characterEncoding=utf8&serverTimezone=Asia/Shanghai&nullCatalogMeansCurrent=true"
)
DASH_NAME = "Charging-BigData-BI"
WIDGET_CUSTOM = load_widget_custom()

VIEWS = [
    ("v1_voltage_current", "SELECT record_hour, avg_pack_voltage, avg_charge_current FROM t_voltage_current ORDER BY record_hour"),
    ("v2_cell_voltage_range", "SELECT record_hour, max_cell_voltage, min_cell_voltage FROM t_cell_voltage_range ORDER BY record_hour"),
    (
        "v3_temperature",
        "SELECT SUBSTRING(record_time, 1, 10) AS record_hour, MAX(max_temperature) AS max_temperature, "
        "MIN(min_temperature) AS min_temperature FROM t_temperature "
        "GROUP BY SUBSTRING(record_time, 1, 10) ORDER BY record_hour",
    ),
    ("v4_energy_capacity", "SELECT record_hour, avg_available_energy, avg_available_capacity FROM t_energy_capacity ORDER BY record_hour"),
    ("v5_charge_current_stats", "SELECT record_hour, avg_charge_current, max_charge_current FROM t_charge_current_stats ORDER BY record_hour"),
    (
        "v6_voltage_current_relation",
        "SELECT record_hour, voltage_change_rate, current_change_rate FROM t_voltage_current_relation "
        "ORDER BY CAST(record_hour AS UNSIGNED)",
    ),
    (
        "v7_soc_temperature",
        "SELECT battery_status, avg_max_temperature, avg_min_temperature, var_max_temperature, var_min_temperature "
        "FROM t_soc_temperature ORDER BY FIELD(battery_status, 'idle', 'charging', 'discharging')",
    ),
]

CHARTS = [
    ("chart_v1", "v1_voltage_current", "v1_voltage_current"),
    ("chart_v2", "v2_cell_voltage_range", "v2_cell_voltage_range"),
    ("chart_v3", "v3_temperature", "v3_temperature"),
    ("chart_v4", "v4_energy_capacity", "v4_energy_capacity"),
    ("chart_v5", "v5_charge_current_stats", "v5_charge_current_stats"),
    ("chart_v6", "v6_voltage_current_relation", "v6_voltage_change_rate"),
    ("chart_v7", "v7_soc_temperature", "v7_battery_status_temperature"),
]

LAYOUT = [
    ("chart_v1", 0, 0, 6, 6),
    ("chart_v2", 6, 0, 6, 6),
    ("chart_v3", 0, 6, 6, 6),
    ("chart_v4", 6, 6, 6, 6),
    ("chart_v5", 0, 12, 6, 6),
    ("chart_v6", 6, 12, 6, 6),
    ("chart_v7", 0, 18, 12, 6),
]


def req(method: str, path: str, token: str | None, body=None) -> dict:
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = token
    data = None if body is None else json.dumps(body).encode()
    request = urllib.request.Request(f"{BASE}{path}", data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=180) as resp:
            raw = resp.read().decode()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"{method} {path} HTTP{e.code}: {e.read().decode(errors='replace')}") from e


def main() -> None:
    login_req = urllib.request.Request(
        f"{BASE}/api/v1/users/login",
        data=json.dumps({"username": USER, "password": PASS}).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(login_req, timeout=60) as resp:
        token = resp.headers.get("Authorization") or resp.headers.get("authorization")
        login = json.loads(resp.read().decode())
    if not token:
        raise SystemExit("login failed: no token")
    org = (login.get("data") or {}).get("orgId") or (req("GET", "/api/v1/orgs", token).get("data") or [{}])[0].get("id")
    print(f"login ok orgId={org}")

    jdbc = {
        "dbType": "MYSQL",
        "url": JDBC,
        "user": "root",
        "password": MYSQL_PW,
        "driverClass": "com.mysql.cj.jdbc.Driver",
        "serverAggregate": False,
        "enableSpecialSQL": False,
        "enableSyncSchemas": True,
        "syncInterval": "60",
        "properties": {},
    }
    sources = {s["name"]: s for s in (req("GET", f"/api/v1/sources?orgId={org}", token).get("data") or [])}
    if "charging_bigdata" in sources:
        sid = sources["charging_bigdata"]["id"]
        req("PUT", f"/api/v1/sources/{sid}", token, {"id": sid, "name": "charging_bigdata", "type": "JDBC", "orgId": org, "config": jdbc})
        print("updated datasource charging_bigdata")
    else:
        req("POST", "/api/v1/data-provider/test", token, {"name": "charging_bigdata", "type": "JDBC", "properties": jdbc})
        sid = req("POST", "/api/v1/sources", token, {"name": "charging_bigdata", "type": "JDBC", "orgId": org, "config": jdbc})["data"]["id"]
        print("created datasource charging_bigdata")

    view_ids: dict[str, str] = {}
    existing = {v["name"]: v for v in (req("GET", f"/api/v1/views?orgId={org}", token).get("data") or []) if not v.get("isFolder")}
    for name, script in VIEWS:
        cols = req("POST", "/api/v1/data-provider/execute/test", token, {"sourceId": sid, "script": script, "scriptType": "SQL", "size": 20})["data"]["columns"]
        model_cols = {}
        for c in cols:
            n = c.get("name")
            if not n or n == "id":
                continue
            model_cols[n[0]] = {"name": n, "type": c.get("type", "STRING"), "category": "UNCATEGORIZED", "path": [n[0]]}
        model = json.dumps({"version": "1.0", "columns": model_cols, "hierarchy": model_cols})
        if name in existing:
            vid = existing[name]["id"]
            req("PUT", f"/api/v1/views/{vid}", token, {"id": vid, "name": name, "orgId": org, "sourceId": sid, "type": "SQL", "script": script, "model": model})
        else:
            vid = req("POST", "/api/v1/views", token, {"name": name, "orgId": org, "sourceId": sid, "type": "SQL", "script": script, "isFolder": False, "model": model})["data"]["id"]
        view_ids[name] = vid
        print(f"view ok: {name}")

    folders = req("GET", f"/api/v1/viz/folders?orgId={org}", token).get("data") or []
    chart_folders = {f["name"]: f for f in folders if f.get("relType") == "DATACHART"}
    chart_ids: dict[str, str] = {}
    for cname, vname, title in CHARTS:
        cfg = CHART_BUILDERS[cname]
        vid = view_ids[vname]
        if cname in chart_folders:
            cid = chart_folders[cname]["relId"]
            req("PUT", f"/api/v1/viz/datacharts/{cid}", token, {"id": cid, "name": cname, "orgId": org, "viewId": vid, "config": cfg})
        else:
            cid = req("POST", "/api/v1/viz/datacharts", token, {"name": cname, "orgId": org, "viewId": vid, "config": cfg})["data"]["id"]
        chart_ids[cname] = cid
        print(f"chart ok: {cname} -> {vname} (styles={len(cfg['chartConfig']['styles'])})")

    dash_folder = next((f for f in folders if f.get("relType") == "DASHBOARD" and DASH_NAME in (f.get("name") or "")), None)
    if not dash_folder:
        dash_folder = req("POST", "/api/v1/viz/dashboards", token, {"name": DASH_NAME, "orgId": org, "index": 1, "config": AUTO_BOARD})["data"]
        folders = req("GET", f"/api/v1/viz/folders?orgId={org}", token).get("data") or []
        dash_folder = next(f for f in folders if f.get("relType") == "DASHBOARD" and f.get("relId") == dash_folder["id"])
    dash_id = dash_folder["relId"]
    dash = req("GET", f"/api/v1/viz/dashboards/{dash_id}", token)["data"]
    delete_ids = [w["id"] for w in (dash.get("widgets") or [])]

    title_by_chart = {c[0]: c[2] for c in CHARTS}
    view_by_chart = {c[0]: c[1] for c in CHARTS}
    widgets = []
    for i, (cname, x, y, w, h) in enumerate(LAYOUT):
        wid = uuid.uuid4().hex
        widgets.append({
            "id": f"linkedChart{wid}",
            "dashboardId": dash_id,
            "datachartId": chart_ids[cname],
            "parentId": "",
            "viewIds": [view_ids[view_by_chart[cname]]],
            "relations": [],
            "config": json.dumps({
                "version": "1.0.0-RC.3",
                "clientId": f"client_{uuid.uuid4().hex}",
                "index": i,
                "name": title_by_chart[cname],
                "boardType": "auto",
                "type": "chart",
                "originalType": "linkedChart",
                "lock": False,
                "content": {},
                "rect": {"x": 0, "y": 0, "width": 400, "height": 300},
                "pRect": {"x": x, "y": y, "width": w, "height": h},
                "customConfig": WIDGET_CUSTOM,
            }),
        })

    req("PUT", f"/api/v1/viz/dashboards/{dash_id}", token, {
        "id": dash_id,
        "name": DASH_NAME,
        "orgId": org,
        "index": 1,
        "config": AUTO_BOARD,
        "widgetToCreate": widgets,
        "widgetToUpdate": [],
        "widgetToDelete": delete_ids,
    })
    req("PUT", f"/api/v1/viz/publish/{dash_id}?vizType=DASHBOARD", token, None)
    for cid in chart_ids.values():
        req("PUT", f"/api/v1/viz/publish/{cid}?vizType=DATACHART", token, None)

    shares = req("GET", f"/api/v1/shares/{dash_id}", token).get("data") or []
    if not shares:
        shares = [req("POST", "/api/v1/shares", token, {"vizType": "DASHBOARD", "vizId": dash_id, "authenticationMode": "NONE"})["data"]]
    share_url = f"{BASE}/shareDashboard/{shares[0]['id']}?type=NONE"

    print(f"DONE dashboard={dash_id}")
    print(f"Login:    {BASE}  ({USER} / {PASS})  ->  {DASH_NAME}")
    print(f"Share:    {share_url}")
    print("Frontend: add to .env.docker then rebuild:")
    print(f"  VITE_DATART_BASE_URL={BASE}")
    print(f"  VITE_DATART_DASHBOARD_URL={share_url}")
    print("  docker compose build frontend && docker compose up -d frontend")


if __name__ == "__main__":
    main()
