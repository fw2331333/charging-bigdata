# -*- coding: utf-8 -*-
"""charging_bigdata 数据字典元数据（与 sql/*.sql 一致，供 xls / Word 生成）。"""

from __future__ import annotations

# (序号, 表名, 中文名, 说明)
TABLE_CATALOG: list[tuple[float, str, str, str]] = [
    (1.0, "t_voltage_current", "电压电流趋势表", "MR v1 每小时平均组电压与充电电流"),
    (2.0, "t_cell_voltage_range", "单体电压范围表", "MR v2 每小时单体电压最高/最低值"),
    (3.0, "t_temperature", "温度趋势表", "MR v3 各时间点最高/最低温度"),
    (4.0, "t_energy_capacity", "能量容量趋势表", "MR v4 每小时平均可用能量与容量"),
    (5.0, "t_charge_current_stats", "充电电流统计表", "MR v5 每小时充电电流均值与峰值"),
    (6.0, "t_voltage_current_relation", "组电压变化率表", "MR v6 按小时统计组电压与充电电流变化率(%)"),
    (7.0, "t_soc_temperature", "电池状态温度表", "MR v7 按 idle/charging/discharging 统计温度均值与方差"),
    (8.0, "t_soc_hourly", "每小时SOC表", "ADS 每小时平均 SOC"),
    (9.0, "t_charging_daily", "日充电次数表", "ADS 每日充电会话次数"),
    (10.0, "t_charging_monthly", "月充电次数表", "ADS 每月充电会话次数"),
    (11.0, "t_charge_rate_hourly", "小时充电速率表", "ADS 各小时平均充电速率"),
    (12.0, "t_soc_heatmap", "SOC热力图表", "ADS 日×小时 SOC 矩阵"),
    (13.0, "sys_user", "系统用户表", "Web 登录用户与角色"),
    (14.0, "sys_refresh_token", "刷新令牌表", "JWT Refresh Token 轮换存储"),
    (15.0, "sys_token_blacklist", "令牌黑名单表", "已吊销 Access Token jti"),
    (16.0, "sys_email_verification_token", "邮件验证令牌表", "邮箱验证与密码重置令牌"),
    (17.0, "sys_profile_otp", "个人资料验证码表", "修改密码等邮箱 OTP"),
    (18.0, "bi_chart_view", "BI图表配置表", "MR 七图前端展示元数据"),
]

# 字段行：[字段, 类型, 长度, 非空(是/否), 键(主/外/索引), 备注]
TABLE_FIELDS: dict[str, list[list[str]]] = {
    "t_voltage_current": [
        ["id", "int", "", "是", "主", "自增主键"],
        ["record_hour", "varchar", "20", "是", "唯一", "小时键 yyyyMMddHH"],
        ["avg_pack_voltage", "double", "", "否", "", "平均组电压(V)"],
        ["avg_charge_current", "double", "", "否", "", "平均充电电流(A)"],
    ],
    "t_cell_voltage_range": [
        ["id", "int", "", "是", "主", "自增主键"],
        ["record_hour", "varchar", "20", "是", "唯一", "小时键 yyyyMMddHH"],
        ["max_cell_voltage", "double", "", "否", "", "最高单体电压(V)"],
        ["min_cell_voltage", "double", "", "否", "", "最低单体电压(V)"],
    ],
    "t_temperature": [
        ["id", "int", "", "是", "主", "自增主键"],
        ["record_time", "varchar", "20", "是", "唯一", "时间键 yyyyMMddHHmmss"],
        ["max_temperature", "double", "", "否", "", "最高温度(℃)"],
        ["min_temperature", "double", "", "否", "", "最低温度(℃)"],
    ],
    "t_energy_capacity": [
        ["id", "int", "", "是", "主", "自增主键"],
        ["record_hour", "varchar", "20", "是", "唯一", "小时键 yyyyMMddHH"],
        ["avg_available_energy", "double", "", "否", "", "平均可用能量(kW)"],
        ["avg_available_capacity", "double", "", "否", "", "平均可用容量(Ah)"],
    ],
    "t_charge_current_stats": [
        ["id", "int", "", "是", "主", "自增主键"],
        ["record_hour", "varchar", "20", "是", "唯一", "小时键 yyyyMMddHH"],
        ["avg_charge_current", "double", "", "否", "", "平均充电电流(A)"],
        ["max_charge_current", "double", "", "否", "", "最大充电电流(A)"],
    ],
    "t_voltage_current_relation": [
        ["id", "int", "", "是", "主", "自增主键"],
        ["record_hour", "varchar", "20", "是", "唯一", "小时键 HH(00-23)"],
        ["voltage_change_rate", "double", "", "否", "", "组电压变化率(%)"],
        ["current_change_rate", "double", "", "否", "", "充电电流变化率(%)"],
    ],
    "t_soc_temperature": [
        ["id", "int", "", "是", "主", "自增主键"],
        ["battery_status", "varchar", "20", "是", "唯一", "idle/charging/discharging"],
        ["avg_max_temperature", "double", "", "否", "", "平均最高温度(℃)"],
        ["avg_min_temperature", "double", "", "否", "", "平均最低温度(℃)"],
        ["var_max_temperature", "double", "", "否", "", "最高温度方差"],
        ["var_min_temperature", "double", "", "否", "", "最低温度方差"],
    ],
    "t_soc_hourly": [
        ["id", "int", "", "是", "主", "自增主键"],
        ["time_key", "varchar", "20", "是", "唯一", "yyyyMMddHH"],
        ["avg_soc", "double", "", "是", "", "每小时平均 SOC(%)"],
    ],
    "t_charging_daily": [
        ["id", "int", "", "是", "主", "自增主键"],
        ["record_date", "varchar", "10", "是", "唯一", "yyyyMMdd"],
        ["charge_count", "int", "11", "是", "", "当日充电次数"],
    ],
    "t_charging_monthly": [
        ["id", "int", "", "是", "主", "自增主键"],
        ["record_month", "varchar", "7", "是", "唯一", "yyyyMM"],
        ["charge_count", "int", "11", "是", "", "当月充电次数"],
    ],
    "t_charge_rate_hourly": [
        ["id", "int", "", "是", "主", "自增主键"],
        ["hour_key", "varchar", "4", "是", "唯一", "小时 HH"],
        ["avg_rate", "double", "", "是", "", "平均充电速率(%SOC/分钟)"],
    ],
    "t_soc_heatmap": [
        ["id", "int", "", "是", "主", "自增主键"],
        ["record_day", "varchar", "10", "是", "联合唯一", "yyyyMMdd"],
        ["hour_key", "varchar", "4", "是", "联合唯一", "小时 HH"],
        ["avg_soc", "double", "", "是", "", "该日该小时平均 SOC"],
    ],
    "sys_user": [
        ["id", "int", "", "是", "主", "用户 ID"],
        ["username", "varchar", "50", "是", "唯一", "登录用户名"],
        ["email", "varchar", "100", "否", "唯一", "登录邮箱"],
        ["password_hash", "varchar", "255", "是", "", "bcrypt 哈希"],
        ["role", "varchar", "20", "是", "索引", "admin / user"],
        ["is_active", "tinyint", "1", "是", "", "1 启用 0 禁用"],
        ["email_verified", "tinyint", "1", "是", "", "1 已验证 0 待验证"],
        ["created_at", "datetime", "", "是", "", "创建时间"],
        ["updated_at", "datetime", "", "是", "", "更新时间"],
    ],
    "sys_refresh_token": [
        ["id", "bigint", "", "是", "主", "自增主键"],
        ["username", "varchar", "50", "是", "索引", "所属用户名"],
        ["token_hash", "varchar", "64", "是", "唯一", "Refresh Token SHA256"],
        ["expires_at", "datetime", "", "是", "索引", "过期时间"],
        ["revoked", "tinyint", "1", "是", "", "1 已吊销 0 有效"],
        ["created_at", "datetime", "", "是", "", "创建时间"],
    ],
    "sys_token_blacklist": [
        ["id", "bigint", "", "是", "主", "自增主键"],
        ["token_jti", "varchar", "64", "是", "唯一", "JWT jti"],
        ["expires_at", "datetime", "", "是", "", "令牌过期时间"],
        ["created_at", "datetime", "", "是", "", "写入时间"],
    ],
    "sys_email_verification_token": [
        ["id", "bigint", "", "是", "主", "自增主键"],
        ["user_id", "int", "", "是", "外键", "sys_user.id"],
        ["token_hash", "varchar", "64", "是", "唯一", "令牌 SHA256"],
        ["purpose", "varchar", "32", "是", "索引", "verify_email / reset_password"],
        ["expires_at", "datetime", "", "是", "索引", "过期时间"],
        ["created_at", "datetime", "", "是", "", "创建时间"],
    ],
    "sys_profile_otp": [
        ["id", "bigint", "", "是", "主", "自增主键"],
        ["user_id", "int", "", "是", "外键", "sys_user.id"],
        ["code_hash", "varchar", "64", "是", "", "验证码 SHA256"],
        ["purpose", "varchar", "32", "是", "", "默认 change_password"],
        ["expires_at", "datetime", "", "是", "", "过期时间"],
        ["used", "tinyint", "1", "是", "", "1 已使用 0 未使用"],
        ["created_at", "datetime", "", "是", "", "创建时间"],
    ],
    "bi_chart_view": [
        ["id", "int", "", "是", "主", "自增主键"],
        ["chart_key", "varchar", "16", "是", "唯一", "图表键 v1~v7/p1 等"],
        ["title", "varchar", "128", "是", "", "图表标题"],
        ["chart_type", "varchar", "32", "是", "", "line/bar/scatter 等"],
        ["data_source", "varchar", "128", "是", "", "API 路径或表名"],
        ["drill_route", "varchar", "64", "否", "", "下钻路由"],
        ["grid_area", "varchar", "16", "否", "", "栅格区域"],
        ["sort_order", "int", "", "是", "", "排序序号"],
        ["enabled", "tinyint", "1", "是", "", "1 启用 0 禁用"],
        ["updated_at", "datetime", "", "是", "", "更新时间"],
    ],
}

FIELD_HEADERS = ["字段", "类型", "长度", "非空", "键", "备注"]
