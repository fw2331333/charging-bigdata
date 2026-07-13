#!/usr/bin/env bash
# 一键修复 Datart：数据源 + 视图 + 七图图表 + Dashboard 排版
# 默认 admin/123456  mysql/Charging@2026
set -euo pipefail
export DATART_URL="${DATART_URL:-http://127.0.0.1:8088}"
export DATART_USER="${DATART_USER:-admin}"
export DATART_PASSWORD="${DATART_PASSWORD:-123456}"
export MYSQL_HOST="${MYSQL_HOST:-mysql}"
export MYSQL_PASSWORD="${MYSQL_PASSWORD:-Charging@2026}"
python3 <<'PY'
import json, os, uuid, urllib.error, urllib.request

BASE = os.environ.get("DATART_URL", "http://127.0.0.1:8088").rstrip("/")
USER = os.environ.get("DATART_USER", "admin")
PASS = os.environ.get("DATART_PASSWORD", "123456")
MYSQL_HOST = os.environ.get("MYSQL_HOST", "mysql")
MYSQL_PW = os.environ.get("MYSQL_PASSWORD", "Charging@2026")
JDBC = f"jdbc:mysql://{MYSQL_HOST}:3306/charging_bigdata?useUnicode=true&characterEncoding=utf8&serverTimezone=Asia/Shanghai&nullCatalogMeansCurrent=true"
DASH_NAME = "Charging-BigData-BI"

VIEWS = [
    ("v1_voltage_current", "SELECT record_hour, avg_pack_voltage, avg_charge_current FROM t_voltage_current ORDER BY record_hour"),
    ("v2_cell_voltage_range", "SELECT record_hour, max_cell_voltage, min_cell_voltage FROM t_cell_voltage_range ORDER BY record_hour"),
    ("v3_temperature", "SELECT SUBSTRING(record_time, 1, 10) AS record_hour, MAX(max_temperature) AS max_temperature, MIN(min_temperature) AS min_temperature FROM t_temperature GROUP BY SUBSTRING(record_time, 1, 10) ORDER BY record_hour"),
    ("v4_energy_capacity", "SELECT record_hour, avg_available_energy, avg_available_capacity FROM t_energy_capacity ORDER BY record_hour"),
    ("v5_charge_current_stats", "SELECT record_hour, avg_charge_current, max_charge_current FROM t_charge_current_stats ORDER BY record_hour"),
    ("v6_voltage_current_relation", "SELECT record_hour, voltage_change_rate, current_change_rate FROM t_voltage_current_relation ORDER BY CAST(record_hour AS UNSIGNED)"),
    ("v7_soc_temperature", "SELECT battery_status, avg_max_temperature, avg_min_temperature, var_max_temperature, var_min_temperature FROM t_soc_temperature ORDER BY FIELD(battery_status, 'idle', 'charging', 'discharging')"),
]

CHARTS = [
    ("chart_v1", "v1_voltage_current", "v1_voltage_current", "cluster-column-chart", "record_hour", ["avg_pack_voltage", "avg_charge_current"], []),
    ("chart_v2", "v2_cell_voltage_range", "v2_cell_voltage_range", "cluster-column-chart", "record_hour", ["max_cell_voltage", "min_cell_voltage"], []),
    ("chart_v3", "v3_temperature", "v3_temperature", "line-chart", "record_hour", ["max_temperature", "min_temperature"], []),
    ("chart_v4", "v4_energy_capacity", "v4_energy_capacity", "stack-area-chart", "record_hour", ["avg_available_energy", "avg_available_capacity"], []),
    ("chart_v5", "v5_charge_current_stats", "v5_charge_current_stats", "cluster-column-chart", "record_hour", ["max_charge_current", "avg_charge_current"], []),
    ("chart_v6", "v6_voltage_current_relation", "v6_voltage_change_rate", "line-chart", "record_hour", ["voltage_change_rate", "current_change_rate"], []),
    ("chart_v7", "v7_soc_temperature", "v7_battery_status_temperature", "double-y", "battery_status", ["avg_max_temperature", "avg_min_temperature"], ["var_max_temperature", "var_min_temperature"]),
]

LAYOUT = [
    ("chart_v1", 0, 0, 6, 6), ("chart_v2", 6, 0, 6, 6),
    ("chart_v3", 0, 6, 6, 6), ("chart_v4", 6, 6, 6, 6),
    ("chart_v5", 0, 12, 6, 6), ("chart_v6", 6, 12, 6, 6),
    ("chart_v7", 0, 18, 12, 6),
]

AUTO_BOARD = '{"type":"auto","version":"1.0.0-RC.3","jsonConfig":{"props":[{"label":"basic.basic","key":"basic","comType":"group","rows":[{"label":"basic.initialQuery","key":"initialQuery","value":true,"comType":"switch"},{"label":"basic.allowOverlap","key":"allowOverlap","value":false,"comType":"switch"}]}],"i18ns":[]}}'
WIDGET_CUSTOM = {"props":[],"interactions":[]}


def req(method, path, token, body=None):
    h = {"Content-Type": "application/json"}
    if token:
        h["Authorization"] = token
    data = None if body is None else json.dumps(body).encode()
    r = urllib.request.Request(f"{BASE}{path}", data=data, headers=h, method=method)
    try:
        with urllib.request.urlopen(r, timeout=180) as resp:
            raw = resp.read().decode()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"{method} {path} HTTP{e.code}: {e.read().decode(errors='replace')}") from e


def uid():
    return uuid.uuid4().hex


def field(col, typ="STRING"):
    return {"colName": col, "type": typ, "category": "field", "uid": uid(), "aggregate": ""}


def metric(col):
    f = field(col, "NUMERIC")
    f["format"] = {"type": "numeric", "numeric": {"decimalPlaces": 2, "unitKey": "none", "useThousandSeparator": False, "prefix": "", "suffix": ""}}
    return f


def chart_config(graph_id, dim, metrics, metrics_r=None):
    datas = [
        {"label": "dimension", "key": "dimension", "type": "group", "rows": [field(dim)]},
    ]
    if graph_id == "double-y":
        datas += [
            {"label": "axis.y.left", "key": "metricsL", "type": "aggregate", "rows": [metric(m) for m in metrics]},
            {"label": "axis.y.right", "key": "metricsR", "type": "aggregate", "rows": [metric(m) for m in (metrics_r or [])]},
        ]
    else:
        datas.append({"label": "metrics", "key": "metrics", "type": "aggregate", "rows": [metric(m) for m in metrics]})
    return {
        "aggregation": False,
        "chartGraphId": graph_id,
        "computedFields": [],
        "chartConfig": {"datas": datas, "styles": [], "settings": [], "interactions": [], "i18ns": []},
    }


# login
r = urllib.request.Request(f"{BASE}/api/v1/users/login", data=json.dumps({"username": USER, "password": PASS}).encode(), headers={"Content-Type": "application/json"}, method="POST")
with urllib.request.urlopen(r, timeout=60) as resp:
    token = resp.headers.get("Authorization") or resp.headers.get("authorization")
    login = json.loads(resp.read().decode())
if not token:
    raise SystemExit("login failed: no token")
org = (login.get("data") or {}).get("orgId") or (req("GET", "/api/v1/orgs", token).get("data") or [{}])[0].get("id")
print(f"login ok orgId={org}")

# datasource
jdbc = {"dbType": "MYSQL", "url": JDBC, "user": "root", "password": MYSQL_PW, "driverClass": "com.mysql.cj.jdbc.Driver", "serverAggregate": False, "enableSpecialSQL": False, "enableSyncSchemas": True, "syncInterval": "60", "properties": {}}
sources = {s["name"]: s for s in (req("GET", f"/api/v1/sources?orgId={org}", token).get("data") or [])}
if "charging_bigdata" in sources:
    sid = sources["charging_bigdata"]["id"]
    req("PUT", f"/api/v1/sources/{sid}", token, {"id": sid, "name": "charging_bigdata", "type": "JDBC", "orgId": org, "config": jdbc})
    print("updated datasource charging_bigdata")
else:
    req("POST", "/api/v1/data-provider/test", token, {"name": "charging_bigdata", "type": "JDBC", "properties": jdbc})
    sid = req("POST", "/api/v1/sources", token, {"name": "charging_bigdata", "type": "JDBC", "orgId": org, "config": jdbc})["data"]["id"]
    print("created datasource charging_bigdata")

# views
view_ids = {}
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

# datacharts
folders = req("GET", f"/api/v1/viz/folders?orgId={org}", token).get("data") or []
chart_folders = {f["name"]: f for f in folders if f.get("relType") == "DATACHART"}
chart_ids = {}
for cname, vname, title, graph, dim, met, met_r in CHARTS:
    cfg = chart_config(graph, dim, met, met_r)
    vid = view_ids[vname]
    if cname in chart_folders:
        cid = chart_folders[cname]["relId"]
        req("PUT", f"/api/v1/viz/datacharts/{cid}", token, {"id": cid, "name": cname, "orgId": org, "viewId": vid, "config": cfg})
    else:
        cid = req("POST", "/api/v1/viz/datacharts", token, {"name": cname, "orgId": org, "viewId": vid, "config": cfg})["data"]["id"]
    chart_ids[cname] = cid
    print(f"chart ok: {cname} -> {vname}")

# dashboard
dash_folder = next((f for f in folders if f.get("relType") == "DASHBOARD" and DASH_NAME in (f.get("name") or "")), None)
if not dash_folder:
    dash_folder = req("POST", "/api/v1/viz/dashboards", token, {"name": DASH_NAME, "orgId": org, "index": 1, "config": AUTO_BOARD})["data"]
    folders = req("GET", f"/api/v1/viz/folders?orgId={org}", token).get("data") or []
    dash_folder = next(f for f in folders if f.get("relType") == "DASHBOARD" and f.get("relId") == dash_folder["id"])
dash_id = dash_folder["relId"]
dash = req("GET", f"/api/v1/viz/dashboards/{dash_id}", token)["data"]
delete_ids = [w["id"] for w in (dash.get("widgets") or [])]
widgets = []
for i, (cname, x, y, w, h) in enumerate(LAYOUT):
    wid = uuid.uuid4().hex
    widgets.append({
        "id": f"linkedChart{wid}",
        "dashboardId": dash_id,
        "datachartId": chart_ids[cname],
        "parentId": "",
        "viewIds": [view_ids[next(v for c, v, *_ in CHARTS if c == cname)]],
        "relations": [],
        "config": json.dumps({
            "version": "1.0.0-RC.3", "clientId": f"client_{uuid.uuid4().hex}", "index": i,
            "name": next(t for c, _, t, *_ in CHARTS if c == cname),
            "boardType": "auto", "type": "chart", "originalType": "linkedChart", "lock": False,
            "content": {}, "rect": {"x": 0, "y": 0, "width": 400, "height": 300},
            "pRect": {"x": x, "y": y, "width": w, "height": h},
            "customConfig": WIDGET_CUSTOM,
        }),
    })
req("PUT", f"/api/v1/viz/dashboards/{dash_id}", token, {
    "id": dash_id, "name": DASH_NAME, "orgId": org, "index": 1, "config": AUTO_BOARD,
    "widgetToCreate": widgets, "widgetToUpdate": [], "widgetToDelete": delete_ids,
})
req("PUT", f"/api/v1/viz/publish/{dash_id}?vizType=DASHBOARD", token, None)
for cid in chart_ids.values():
    req("PUT", f"/api/v1/viz/publish/{cid}?vizType=DATACHART", token, None)
print(f"DONE dashboard={dash_id}")
print(f"Open {BASE} -> {DASH_NAME}  (admin / {PASS})  Ctrl+Shift+R")
PY
