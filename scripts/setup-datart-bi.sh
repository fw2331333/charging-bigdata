#!/usr/bin/env bash
# 在 ECS/Linux 上用 admin 更新 Datart 数据源 + v1~v7 视图，并尝试重建大屏。
# 用法（在服务器项目根目录）：
#   export DATART_PASSWORD='你的admin密码'
#   bash scripts/setup-datart-bi.sh
#
# 可选环境变量：
#   DATART_URL=http://127.0.0.1:8088
#   DATART_USER=admin
#   MYSQL_HOST=mysql
#   MYSQL_PASSWORD=Charging@2026
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

DATART_URL="${DATART_URL:-http://127.0.0.1:8088}"
DATART_USER="${DATART_USER:-admin}"
DATART_PASSWORD="${DATART_PASSWORD:-123456}"
MYSQL_HOST="${MYSQL_HOST:-mysql}"
MYSQL_PORT="${MYSQL_PORT:-3306}"
MYSQL_USER="${MYSQL_USER:-root}"
MYSQL_PASSWORD="${MYSQL_PASSWORD:-Charging@2026}"
MYSQL_DATABASE="${MYSQL_DATABASE:-charging_bigdata}"
ORG_ID="${DATART_ORG_ID:-}"

if [[ -z "${DATART_PASSWORD}" ]]; then
  echo "请设置 admin 密码: export DATART_PASSWORD='...'" >&2
  exit 1
fi

echo "Datart setup -> $DATART_URL (user=$DATART_USER)"

export DATART_URL DATART_USER DATART_PASSWORD MYSQL_HOST MYSQL_PORT MYSQL_USER MYSQL_PASSWORD MYSQL_DATABASE ORG_ID
python3 <<'PY'
import json
import os
import sys
import urllib.error
import urllib.request

BASE = os.environ["DATART_URL"].rstrip("/")
USER = os.environ["DATART_USER"]
PASS = os.environ["DATART_PASSWORD"]
ORG = os.environ.get("ORG_ID") or ""
MYSQL_HOST = os.environ["MYSQL_HOST"]
MYSQL_PORT = os.environ["MYSQL_PORT"]
MYSQL_USER = os.environ["MYSQL_USER"]
MYSQL_PASSWORD = os.environ["MYSQL_PASSWORD"]
MYSQL_DB = os.environ["MYSQL_DATABASE"]

JDBC = (
    f"jdbc:mysql://{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
    "?useUnicode=true&characterEncoding=utf8&serverTimezone=Asia/Shanghai&nullCatalogMeansCurrent=true"
)

VIEW_DEFS = [
    ("v1_voltage_current", "SELECT record_hour, avg_pack_voltage, avg_charge_current FROM t_voltage_current ORDER BY record_hour"),
    ("v2_cell_voltage_range", "SELECT record_hour, max_cell_voltage, min_cell_voltage FROM t_cell_voltage_range ORDER BY record_hour"),
    ("v3_temperature", "SELECT SUBSTRING(record_time, 1, 10) AS record_hour, MAX(max_temperature) AS max_temperature, MIN(min_temperature) AS min_temperature FROM t_temperature GROUP BY SUBSTRING(record_time, 1, 10) ORDER BY record_hour"),
    ("v4_energy_capacity", "SELECT record_hour, avg_available_energy, avg_available_capacity FROM t_energy_capacity ORDER BY record_hour"),
    ("v5_charge_current_stats", "SELECT record_hour, avg_charge_current, max_charge_current FROM t_charge_current_stats ORDER BY record_hour"),
    ("v6_voltage_current_relation", "SELECT record_hour, voltage_change_rate, current_change_rate FROM t_voltage_current_relation ORDER BY CAST(record_hour AS UNSIGNED)"),
    ("v7_soc_temperature", "SELECT battery_status, avg_max_temperature, avg_min_temperature, var_max_temperature, var_min_temperature FROM t_soc_temperature ORDER BY FIELD(battery_status, 'idle', 'charging', 'discharging')"),
]

SOURCE_NAMES = ["charging_bigdata", "cbp_charging_bigdata"]


def req(method, path, token, body=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = token
    data = None if body is None else json.dumps(body).encode("utf-8")
    r = urllib.request.Request(f"{BASE}{path}", data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(r, timeout=120) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        msg = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"{method} {path} -> HTTP {e.code}: {msg}") from e


def login():
    r = urllib.request.Request(
        f"{BASE}/api/v1/users/login",
        data=json.dumps({"username": USER, "password": PASS}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(r, timeout=60) as resp:
        token = resp.headers.get("Authorization") or resp.headers.get("authorization")
        body = json.loads(resp.read().decode("utf-8"))
    if not token:
        raise RuntimeError("login ok but no Authorization header")
    if not body.get("success", True) and body.get("errCode") not in (0, None):
        raise RuntimeError(f"login failed: {body}")
    return token, body


def resolve_org(token, login_body):
    org = ORG
    data = login_body.get("data") or {}
    if not org:
        org = data.get("orgId") or ""
    if not org:
        orgs = req("GET", "/api/v1/orgs", token).get("data") or []
        if orgs:
            org = orgs[0].get("id", "")
    if not org:
        raise RuntimeError("cannot resolve orgId; set DATART_ORG_ID=...")
    print(f"orgId={org}")
    return org


def jdbc_config():
    return {
        "dbType": "MYSQL",
        "url": JDBC,
        "user": MYSQL_USER,
        "password": MYSQL_PASSWORD,
        "driverClass": "com.mysql.cj.jdbc.Driver",
        "serverAggregate": False,
        "enableSpecialSQL": False,
        "enableSyncSchemas": True,
        "syncInterval": "60",
        "properties": {},
    }


def build_model(columns):
    cols = {}
    for c in columns:
        name = c.get("name")
        if not name or name == "id":
            continue
        key = name[0]
        cols[key] = {
            "name": name,
            "type": c.get("type", "STRING"),
            "category": "UNCATEGORIZED",
            "path": [key],
        }
    return json.dumps({"version": "1.0", "columns": cols, "hierarchy": cols}, ensure_ascii=False)


def ensure_source(token, org):
    sources = req("GET", f"/api/v1/sources?orgId={org}", token).get("data") or []
    by_name = {s.get("name"): s for s in sources}

    for name in SOURCE_NAMES:
        if name in by_name:
            sid = by_name[name]["id"]
            print(f"update datasource: {name} ({sid})")
            req("PUT", f"/api/v1/sources/{sid}", token, {
                "id": sid,
                "name": name,
                "type": "JDBC",
                "orgId": org,
                "config": jdbc_config(),
            })
            return sid, name

    name = SOURCE_NAMES[0]
    print(f"create datasource: {name}")
    test = {"name": name, "type": "JDBC", "properties": jdbc_config()}
    req("POST", "/api/v1/data-provider/test", token, test)
    created = req("POST", "/api/v1/sources", token, {
        "name": name,
        "type": "JDBC",
        "orgId": org,
        "config": jdbc_config(),
    }).get("data") or {}
    return created["id"], name


def upsert_views(token, org, source_id):
    existing = req("GET", f"/api/v1/views?orgId={org}", token).get("data") or []
    by_name = {v.get("name"): v for v in existing if not v.get("isFolder")}

    for name, script in VIEW_DEFS:
        cols = req("POST", "/api/v1/data-provider/execute/test", token, {
            "sourceId": source_id,
            "script": script,
            "scriptType": "SQL",
            "size": 20,
        }).get("data", {}).get("columns") or []
        model = build_model(cols)
        if name in by_name:
            vid = by_name[name]["id"]
            print(f"update view: {name}")
            req("PUT", f"/api/v1/views/{vid}", token, {
                "id": vid,
                "name": name,
                "orgId": org,
                "sourceId": source_id,
                "type": "SQL",
                "script": script,
                "model": model,
            })
        else:
            print(f"create view: {name}")
            req("POST", "/api/v1/views", token, {
                "name": name,
                "orgId": org,
                "sourceId": source_id,
                "type": "SQL",
                "script": script,
                "isFolder": False,
                "model": model,
            })


token, login_body = login()
org = resolve_org(token, login_body)
source_id, source_name = ensure_source(token, org)
upsert_views(token, org, source_id)
print(f"OK: datasource={source_name}, views={len(VIEW_DEFS)}")
PY

echo ""
echo "=== 尝试重建 Dashboard 七图（需 pwsh）==="
if command -v pwsh >/dev/null 2>&1; then
  pwsh "$ROOT/scripts/build-datart-dashboard.ps1" \
    -DatartUrl "$DATART_URL" \
    -DatartUser "$DATART_USER" \
    -DatartPassword "$DATART_PASSWORD"
else
  echo "未安装 PowerShell。安装后重建大屏："
  echo "  sudo apt update && sudo apt install -y powershell"
  echo "  export DATART_PASSWORD='...'"
  echo "  pwsh scripts/build-datart-dashboard.ps1 -DatartUrl $DATART_URL -DatartUser $DATART_USER -DatartPassword \"\$DATART_PASSWORD\""
  echo ""
  echo "视图 SQL 已更新；也可在 Datart 网页里打开 Dashboard 刷新图表。"
fi

echo ""
echo "打开: $DATART_URL  (用户 $DATART_USER)"
