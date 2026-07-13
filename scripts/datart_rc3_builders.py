"""Datart 1.0.0-RC.3 chart / widget config builders (mirrors build-datart-dashboard.ps1)."""
from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
WIDGET_CUSTOM_PATH = SCRIPT_DIR / "datart-linked-widget-custom.json"

FONT_COLOR = "#495057"
SPLIT_LINE_COLOR = "#ced4da"


def _uid() -> str:
    return uuid.uuid4().hex


def load_widget_custom() -> dict[str, Any]:
    with WIDGET_CUSTOM_PATH.open(encoding="utf-8") as f:
        return json.load(f)


AUTO_BOARD = (
    '{"type":"auto","version":"1.0.0-RC.3","jsonConfig":{"props":['
    '{"label":"basic.basic","key":"basic","comType":"group","rows":['
    '{"label":"basic.initialQuery","key":"initialQuery","value":true,"comType":"switch"},'
    '{"label":"basic.allowOverlap","key":"allowOverlap","value":false,"comType":"switch"}]},'
    '{"label":"space.space","key":"space","comType":"group","rows":['
    '{"label":"space.paddingTB","key":"paddingTB","default":14,"value":14,"comType":"inputNumber"},'
    '{"label":"space.paddingLR","key":"paddingLR","default":14,"value":14,"comType":"inputNumber"},'
    '{"label":"space.marginTB","key":"marginTB","default":16,"value":16,"comType":"inputNumber"},'
    '{"label":"space.marginLR","key":"marginLR","default":14,"value":14,"comType":"inputNumber"}]},'
    '{"label":"mSpace.mSpace","key":"mSpace","comType":"group","rows":['
    '{"label":"mSpace.paddingTB","key":"paddingTB","default":14,"value":14,"comType":"inputNumber"},'
    '{"label":"mSpace.paddingLR","key":"paddingLR","default":14,"value":14,"comType":"inputNumber"},'
    '{"label":"mSpace.marginTB","key":"marginTB","default":16,"value":16,"comType":"inputNumber"},'
    '{"label":"mSpace.marginLR","key":"marginLR","default":14,"value":14,"comType":"inputNumber"}]},'
    '{"label":"background.background","key":"background","comType":"group","rows":['
    '{"label":"background.background","key":"background","default":'
    '{"color":"transparent","image":"","size":"100% 100%","repeat":"no-repeat"},'
    '"value":{"color":"transparent","image":"","size":"100% 100%","repeat":"no-repeat"},'
    '"comType":"background"}]}],"i18ns":[]}}'
)


def _font(font_size: str = "9") -> dict[str, Any]:
    return {
        "fontFamily": "PingFang SC",
        "fontSize": font_size,
        "fontWeight": "normal",
        "fontStyle": "normal",
        "color": FONT_COLOR,
    }


def chart_margin_styles() -> dict[str, Any]:
    return {
        "label": "margin",
        "key": "margin",
        "comType": "group",
        "rows": [
            {"label": "viz.palette.style.margin.containLabel", "key": "containLabel", "value": True, "comType": "checkbox"},
            {"label": "viz.palette.style.margin.left", "key": "marginLeft", "value": "12%", "comType": "marginWidth"},
            {"label": "viz.palette.style.margin.right", "key": "marginRight", "value": "4%", "comType": "marginWidth"},
            {"label": "viz.palette.style.margin.top", "key": "marginTop", "value": "11%", "comType": "marginWidth"},
            {"label": "viz.palette.style.margin.bottom", "key": "marginBottom", "value": "18%", "comType": "marginWidth"},
        ],
    }


def x_axis_styles() -> dict[str, Any]:
    return {
        "label": "xAxis.title",
        "key": "xAxis",
        "comType": "group",
        "rows": [
            {"label": "common.rotate", "key": "rotate", "value": 45, "comType": "inputNumber"},
            {"label": "common.showInterval", "key": "showInterval", "value": True, "comType": "checkbox"},
            {"label": "common.interval", "key": "interval", "value": 0, "comType": "inputNumber"},
        ],
    }


def split_line_styles() -> dict[str, Any]:
    return {
        "label": "splitLine.title",
        "key": "splitLine",
        "comType": "group",
        "rows": [
            {"label": "splitLine.showHorizonLine", "key": "showHorizonLine", "value": True, "comType": "checkbox"},
            {
                "label": "common.lineStyle",
                "key": "horizonLineStyle",
                "comType": "line",
                "value": {"type": "dashed", "width": 1, "color": SPLIT_LINE_COLOR},
            },
        ],
    }


def label_styles(show: bool = True, font_size: str = "9") -> dict[str, Any]:
    return {
        "label": "label.title",
        "key": "label",
        "comType": "group",
        "rows": [
            {"label": "label.showLabel", "key": "showLabel", "value": show, "comType": "checkbox"},
            {"label": "label.position", "key": "position", "value": "top", "comType": "labelPosition"},
            {"label": "viz.palette.style.font", "key": "font", "comType": "font", "value": _font(font_size)},
        ],
    }


def bar_styles() -> dict[str, Any]:
    return {
        "label": "bar.title",
        "key": "bar",
        "comType": "group",
        "rows": [
            {"label": "bar.gap", "key": "gap", "value": 0.38, "comType": "inputPercentage"},
            {"label": "bar.width", "key": "width", "value": 0, "comType": "inputNumber"},
        ],
    }


def cartesian_styles(*, show_label: bool = False, with_bar: bool = False) -> list[dict[str, Any]]:
    styles = [chart_margin_styles(), x_axis_styles(), split_line_styles(), label_styles(show_label)]
    if with_bar:
        styles.append(bar_styles())
    return styles


def double_y_styles() -> list[dict[str, Any]]:
    return [chart_margin_styles(), x_axis_styles(), split_line_styles(), label_styles(False)]


def field(col: str, typ: str = "STRING", aggregate: str = "") -> dict[str, Any]:
    return {"colName": col, "type": typ, "category": "field", "uid": _uid(), "aggregate": aggregate}


def metric(col: str, alias: str | None = None) -> dict[str, Any]:
    f = field(col, "NUMERIC")
    if alias:
        f["alias"] = {"name": alias}
    f["format"] = {
        "type": "numeric",
        "numeric": {
            "decimalPlaces": 1,
            "unitKey": "none",
            "useThousandSeparator": False,
            "prefix": "",
            "suffix": "",
        },
    }
    return f


def data_chart_config(graph_id: str, datas: list[dict[str, Any]], styles: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "aggregation": False,
        "chartGraphId": graph_id,
        "computedFields": [],
        "chartConfig": {
            "datas": datas,
            "styles": styles,
            "settings": [],
            "interactions": [],
            "i18ns": [],
        },
    }


def column_chart(dim: str, metrics: list[str], aliases: dict[str, str] | None = None) -> dict[str, Any]:
    aliases = aliases or {}
    return data_chart_config(
        "cluster-column-chart",
        [
            {"label": "dimension", "key": "dimension", "type": "group", "rows": [field(dim)]},
            {
                "label": "metrics",
                "key": "metrics",
                "type": "aggregate",
                "rows": [metric(m, aliases.get(m)) for m in metrics],
            },
        ],
        cartesian_styles(show_label=False, with_bar=True),
    )


def line_chart(dim: str, metrics: list[str], aliases: dict[str, str] | None = None) -> dict[str, Any]:
    aliases = aliases or {}
    return data_chart_config(
        "line-chart",
        [
            {"label": "dimension", "key": "dimension", "type": "group", "rows": [field(dim)]},
            {
                "label": "metrics",
                "key": "metrics",
                "type": "aggregate",
                "rows": [metric(m, aliases.get(m)) for m in metrics],
            },
        ],
        double_y_styles(),
    )


def stack_area_chart(dim: str, metrics: list[str], aliases: dict[str, str] | None = None) -> dict[str, Any]:
    aliases = aliases or {}
    return data_chart_config(
        "stack-area-chart",
        [
            {"label": "dimension", "key": "dimension", "type": "group", "rows": [field(dim)]},
            {
                "label": "metrics",
                "key": "metrics",
                "type": "aggregate",
                "rows": [metric(m, aliases.get(m)) for m in metrics],
            },
        ],
        cartesian_styles(show_label=False),
    )


def double_y_chart(
    dim: str,
    left: list[str],
    right: list[str],
    aliases: dict[str, str] | None = None,
) -> dict[str, Any]:
    aliases = aliases or {}
    return data_chart_config(
        "double-y",
        [
            {"label": "dimension", "key": "dimension", "type": "group", "rows": [field(dim)]},
            {
                "label": "axis.y.left",
                "key": "metricsL",
                "type": "aggregate",
                "rows": [metric(m, aliases.get(m)) for m in left],
            },
            {
                "label": "axis.y.right",
                "key": "metricsR",
                "type": "aggregate",
                "rows": [metric(m, aliases.get(m)) for m in right],
            },
        ],
        double_y_styles(),
    )


CHART_BUILDERS: dict[str, dict[str, Any]] = {
    "chart_v1": column_chart(
        "record_hour",
        ["avg_pack_voltage", "avg_charge_current"],
        {"avg_pack_voltage": "voltage", "avg_charge_current": "current"},
    ),
    "chart_v2": column_chart(
        "record_hour",
        ["max_cell_voltage", "min_cell_voltage"],
        {"max_cell_voltage": "max_V", "min_cell_voltage": "min_V"},
    ),
    "chart_v3": line_chart(
        "record_hour",
        ["max_temperature", "min_temperature"],
        {"max_temperature": "max_T", "min_temperature": "min_T"},
    ),
    "chart_v4": stack_area_chart(
        "record_hour",
        ["avg_available_energy", "avg_available_capacity"],
        {"avg_available_energy": "energy", "avg_available_capacity": "capacity"},
    ),
    "chart_v5": column_chart(
        "record_hour",
        ["max_charge_current", "avg_charge_current"],
        {"max_charge_current": "max_I", "avg_charge_current": "avg_I"},
    ),
    "chart_v6": line_chart(
        "record_hour",
        ["voltage_change_rate", "current_change_rate"],
        {"voltage_change_rate": "V_chg_%", "current_change_rate": "I_chg_%"},
    ),
    "chart_v7": double_y_chart(
        "battery_status",
        ["avg_max_temperature", "avg_min_temperature"],
        ["var_max_temperature", "var_min_temperature"],
        {
            "avg_max_temperature": "avg_max_T",
            "avg_min_temperature": "avg_min_T",
            "var_max_temperature": "var_max_T",
            "var_min_temperature": "var_min_T",
        },
    ),
}
