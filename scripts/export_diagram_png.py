#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""将项目中的 drawio.svg / drawio 导出为 PNG（Edge 无头截图）。"""
from __future__ import annotations

import json
import subprocess
import tempfile
import time
from pathlib import Path

ROOT = Path(r"F:\项目2资料")
SUBMIT = ROOT / "项目资料提交" / "项目资料提交"
ASSETS = Path(__file__).resolve().parent / "assets"
EDGE = Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe")
if not EDGE.exists():
    EDGE = Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe")

# 报告册插图映射：caption 关键字 -> 源文件（相对 SUBMIT）
FIGURE_MAP = {
    "图3.1": SUBMIT / "01.需求分析" / "01.用例图" / "系统总用例图.drawio",
    "图3.2": SUBMIT / "01.需求分析" / "01.用例图" / "Web前端业务用例图.drawio.svg",
    "图3.3": SUBMIT / "01.需求分析" / "01.用例图" / "数据批处理用例图.drawio.svg",
    "图4.1": SUBMIT / "01.需求分析" / "01.用例图" / "系统架构图.drawio",
    "图4.2": SUBMIT / "01.需求分析" / "03.业务流程图" / "端到端主业务流程图.drawio",
    "图4.3": SUBMIT / "01.需求分析" / "04.泳道图" / "用户访问 Web 系统泳道图.drawio",
    "图6.1": SUBMIT / "02.系统设计" / "01.数据库设计" / "02.E-R图" / "MR 与 ADS 逻辑 E-R 图.drawio",
}

# 演示环境页面截图（可选，需公网可访问）
PAGE_FIGURE_URLS = {
    "图5.1": "http://115.29.194.137:8080/login",
    "图5.2": "http://115.29.194.137:8080/",
    "图5.3": "http://115.29.194.137:8080/mr-bi",
    "图5.4": "http://115.29.194.137:8080/predict/soc",
    "图5.5": "http://115.29.194.137:8088",
    "图5.6": "http://115.29.194.137:8080/bda2",
}


def _svg_for_source(src: Path) -> Path | None:
    if not src.exists():
        return None
    if src.suffix.lower() == ".svg":
        return src
    sibling = src.with_suffix(src.suffix + ".svg")
    if sibling.exists():
        return sibling
    svg_only = src.parent / (src.stem + ".drawio.svg")
    if svg_only.exists():
        return svg_only
    return None


def export_svg_to_png(svg_path: Path, out_path: Path, width: int = 1200) -> bool:
    if not EDGE.exists():
        print("Edge not found, skip", svg_path.name)
        return False
    out_path.parent.mkdir(parents=True, exist_ok=True)
    uri = svg_path.resolve().as_uri()
    html = (
        "<!DOCTYPE html><html><head><meta charset='utf-8'>"
        "<style>html,body{margin:0;padding:8px;background:#fff}</style></head>"
        f"<body><img src='{uri}' style='width:{width}px'></body></html>"
    )
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
        f.write(html)
        html_path = Path(f.name)
    cmd = [
        str(EDGE),
        "--headless",
        "--disable-gpu",
        "--hide-scrollbars",
        f"--window-size={width},900",
        f"--screenshot={out_path.resolve()}",
        html_path.resolve().as_uri(),
    ]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=45, errors="ignore")
        ok = r.returncode == 0 and out_path.exists() and out_path.stat().st_size > 1000
        if not ok:
            print("fail", svg_path.name, r.stderr[:200] if r.stderr else r.stdout[:200])
        return ok
    finally:
        html_path.unlink(missing_ok=True)


def export_drawio_to_png(drawio_path: Path, out_path: Path, width: int = 1200) -> bool:
    if not EDGE.exists() or not drawio_path.exists():
        return False
    xml = drawio_path.read_text(encoding="utf-8")
    payload = json.dumps(
        {"highlight": "#0000ff", "nav": False, "resize": True, "toolbar": "", "xml": xml},
        ensure_ascii=False,
    )
    payload_attr = payload.replace("&", "&amp;").replace('"', "&quot;")
    html = (
        "<!DOCTYPE html><html><head><meta charset='utf-8'>"
        "<style>html,body{margin:0;padding:12px;background:#fff}"
        f".mxgraph{{max-width:{width}px;min-height:600px}}</style></head><body>"
        f'<div class="mxgraph" data-mxgraph="{payload_attr}"></div>'
        "<script src='https://viewer.diagrams.net/js/viewer-static.min.js'></script>"
        "</body></html>"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
        f.write(html)
        html_path = Path(f.name)
    cmd = [
        str(EDGE),
        "--headless",
        "--disable-gpu",
        "--hide-scrollbars",
        f"--window-size={width},1000",
        "--run-all-compositor-stages-before-draw",
        "--virtual-time-budget=15000",
        f"--screenshot={out_path.resolve()}",
        html_path.resolve().as_uri(),
    ]
    try:
        subprocess.run(cmd, capture_output=True, timeout=60, errors="ignore")
        time.sleep(1)
        return out_path.exists() and out_path.stat().st_size > 1000
    finally:
        html_path.unlink(missing_ok=True)


def export_source_to_png(src: Path, out_path: Path) -> bool:
    svg = _svg_for_source(src)
    if svg:
        return export_svg_to_png(svg, out_path)
    if src.suffix.lower() == ".drawio":
        return export_drawio_to_png(src, out_path)
    return False


def export_url_to_png(url: str, out_path: Path, width: int = 1280) -> bool:
    if not EDGE.exists():
        return False
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        str(EDGE),
        "--headless",
        "--disable-gpu",
        f"--window-size={width},900",
        "--run-all-compositor-stages-before-draw",
        "--virtual-time-budget=12000",
        f"--screenshot={out_path.resolve()}",
        url,
    ]
    try:
        subprocess.run(cmd, capture_output=True, timeout=60, errors="ignore")
        time.sleep(1)
        return out_path.exists() and out_path.stat().st_size > 1000
    except Exception:
        return False


def export_all() -> dict[str, Path]:
    ASSETS.mkdir(parents=True, exist_ok=True)
    result: dict[str, Path] = {}
    for key, src in FIGURE_MAP.items():
        safe = key.replace(".", "_") + ".png"
        out = ASSETS / safe
        if export_source_to_png(src, out):
            result[key] = out
            print("ok", key, "->", out.name, out.stat().st_size)
        else:
            print("missing/fail", key, src)
    for key, url in PAGE_FIGURE_URLS.items():
        safe = key.replace(".", "_") + ".png"
        out = ASSETS / safe
        if out.exists() and out.stat().st_size > 1000:
            result[key] = out
            continue
        if export_url_to_png(url, out):
            result[key] = out
            print("page ok", key, out.stat().st_size)
        else:
            print("page fail", key, url)
    return result


if __name__ == "__main__":
    export_all()
