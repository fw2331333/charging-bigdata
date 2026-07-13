#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成数据字典 .xls（格式对齐公众监督 nep数据字典.xls）。"""
from __future__ import annotations

from pathlib import Path

import xlwt

from submission_data_dict import FIELD_HEADERS, TABLE_CATALOG, TABLE_FIELDS

ROOT = Path(r"F:\项目2资料")
OUT_DIR = ROOT / "项目资料提交" / "项目资料提交" / "02.系统设计" / "01.数据库设计" / "03.数据字典"
OUT_FILE = OUT_DIR / "新能源充电桩大数据分析项目-数据字典.xls"


def _style_header() -> xlwt.XFStyle:
    style = xlwt.XFStyle()
    font = xlwt.Font()
    font.bold = True
    style.font = font
    return style


def _write_index_sheet(wb: xlwt.Workbook, header_style: xlwt.XFStyle) -> None:
    sh = wb.add_sheet("DB一览表")
    headers = ["No", "表名", "中文名", "说明"]
    for c, h in enumerate(headers, start=1):
        sh.write(1, c, h, header_style)
    for r, (no, name, cn, desc) in enumerate(TABLE_CATALOG, start=2):
        sh.write(r, 1, no)
        sh.write(r, 2, name)
        sh.write(r, 3, cn)
        sh.write(r, 4, desc)
    sh.col(1).width = 256 * 6
    sh.col(2).width = 256 * 28
    sh.col(3).width = 256 * 22
    sh.col(4).width = 256 * 40


def _write_table_sheet(wb: xlwt.Workbook, table_name: str, header_style: xlwt.XFStyle) -> None:
    # Excel 表名最长 31 字符
    sheet_name = table_name[:31]
    sh = wb.add_sheet(sheet_name)
    for c, h in enumerate(FIELD_HEADERS, start=1):
        sh.write(1, c, h, header_style)
    rows = TABLE_FIELDS.get(table_name, [])
    for r, row in enumerate(rows, start=2):
        for c, val in enumerate(row, start=1):
            sh.write(r, c, val)
    sh.col(1).width = 256 * 22
    sh.col(2).width = 256 * 12
    sh.col(3).width = 256 * 8
    sh.col(4).width = 256 * 6
    sh.col(5).width = 256 * 10
    sh.col(6).width = 256 * 36


def build() -> Path:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    wb = xlwt.Workbook(encoding="utf-8")
    header_style = _style_header()
    _write_index_sheet(wb, header_style)
    for _, table_name, _, _ in TABLE_CATALOG:
        _write_table_sheet(wb, table_name, header_style)
    wb.save(str(OUT_FILE))
    return OUT_FILE


def main() -> None:
    path = build()
    print(f"Saved: {path}")
    print(f"Sheets: 1 index + {len(TABLE_CATALOG)} tables = {1 + len(TABLE_CATALOG)}")


if __name__ == "__main__":
    main()
