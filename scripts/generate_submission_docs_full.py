#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成项目资料提交完整 Word 文档（宋体），结构与公众监督 NEP 模板对齐。"""
from __future__ import annotations

from pathlib import Path

from submission_data_dict import FIELD_HEADERS, TABLE_CATALOG, TABLE_FIELDS
from submission_doc_expansions import (
    expand_outline_ch4,
    expand_outline_ch5,
    expand_outline_ch6,
    expand_outline_ch7,
    expand_srs_late_chapters,
    expand_srs_mid_chapters,
    expand_srs_ch7_extra,
    expand_training_late_chapters,
)
from docx_builder import (
    add_bullets,
    add_center_title,
    add_h,
    add_p,
    add_placeholder_figure,
    add_table,
    count_doc_chars,
    new_doc,
    save_doc,
)

ROOT = Path(r"F:\项目2资料")
SUBMIT = ROOT / "项目资料提交" / "项目资料提交"

# 字符数下限（不含空格与换行）
MIN_CHARS = {
    "srs": 5500,
    "db": 3500,
    "data_dict": 3500,
    "outline": 7000,
    "deploy": 5000,
    "training": 12000,
    "diagram": 2500,
}

ALL_TABLES_SUMMARY = [
    ["t_voltage_current", "MR", "v1", "每小时平均组电压与充电电流"],
    ["t_cell_voltage_range", "MR", "v2", "每小时单体电压极值"],
    ["t_temperature", "MR", "v3", "时间点最高/最低温度"],
    ["t_energy_capacity", "MR", "v4", "每小时可用能量与容量"],
    ["t_charge_current_stats", "MR", "v5", "每小时充电电流统计"],
    ["t_voltage_current_relation", "MR", "v6", "时间点电压电流关系"],
    ["t_soc_temperature", "MR", "v7", "SOC 分段温度统计"],
    ["t_soc_hourly", "ADS", "-", "每小时平均 SOC"],
    ["t_charging_daily", "ADS", "-", "每日充电次数"],
    ["t_charging_monthly", "ADS", "-", "每月充电次数"],
    ["t_charge_rate_hourly", "ADS", "-", "每小时平均充电速率"],
    ["t_soc_heatmap", "ADS", "-", "SOC 热力图日×小时"],
    ["sys_user", "AUTH", "-", "系统用户与角色"],
    ["sys_refresh_token", "AUTH", "-", "Refresh Token 轮换存储"],
    ["sys_token_blacklist", "AUTH", "-", "JWT 黑名单（可选）"],
    ["sys_email_verification_token", "AUTH", "-", "邮箱验证/重置密码令牌"],
    ["sys_profile_otp", "AUTH", "-", "个人资料邮箱验证码"],
    ["bi_chart_view", "CONFIG", "-", "MR 七图前端配置"],
]

FUNCTIONAL_REQUIREMENTS = [
    ["FR-01", "HDFS 数据准备", "P0", "创建 /Car/ 目录并上传 4 个 CSV", "hdfs dfs -ls /Car 显示 4 文件"],
    ["FR-02", "MapReduce v1 电压电流", "P0", "按小时聚合 pack_voltage 与 charge_current 均值", "输出至 t_voltage_current"],
    ["FR-03", "MapReduce v2 单体电压", "P0", "按小时统计 max/min cell voltage", "输出至 t_cell_voltage_range"],
    ["FR-04", "MapReduce v3 温度趋势", "P0", "按时间点统计最高/最低温度", "输出至 t_temperature"],
    ["FR-05", "MapReduce v4 能量容量", "P0", "按小时平均可用能量与容量", "输出至 t_energy_capacity"],
    ["FR-06", "MapReduce v5 充电电流", "P0", "按小时平均与最大充电电流", "输出至 t_charge_current_stats"],
    ["FR-07", "MapReduce v6 电压电流关系", "P0", "按时间点记录组电压与充电电流", "输出至 t_voltage_current_relation"],
    ["FR-08", "MapReduce v7 SOC 温度", "P0", "按 SOC 分段统计平均温度", "输出至 t_soc_temperature"],
    ["FR-09", "MR 结果入库", "P0", "load_mr_to_mysql.py UPSERT 七张 MR 表", "MySQL 可查询全部指标"],
    ["FR-10", "ADS 汇总写入", "P1", "Spark/Python ETL 写入 5 张 ADS 表", "大屏 API 可读"],
    ["FR-11", "BI 看板", "P1", "Datart 连接 charging_bigdata 展示 MR 视图", "电压/温度/SOC 图表可见"],
    ["FR-12", "SOC 趋势分析", "P1", "analyze_soc.py 生成折线图", "charts/soc_hourly.png"],
    ["FR-13", "充电次数分析", "P1", "日/月充电次数统计图", "charging_daily/monthly"],
    ["FR-14", "充电速率分析", "P1", "按小时平均充电速率", "charge_rate_hourly"],
    ["FR-15", "SOC 热力图", "P1", "日×小时 SOC 热力矩阵", "t_soc_heatmap"],
    ["FR-16", "费用预测 ML", "P0", "线性回归与 XGBoost 选优", "POST /api/v1/predict/fee"],
    ["FR-17", "时长预测 ML", "P0", "充电时长回归模型", "POST /api/v1/predict/duration"],
    ["FR-18", "平台预测 ML", "P0", "充电平台分类模型", "POST /api/v1/predict/platform"],
    ["FR-19", "SOC 预测 ML", "P0", "目标 SOC 回归模型", "POST /api/v1/predict/soc"],
    ["FR-20", "用户注册登录", "P0", "邮箱注册、双 Token JWT、bcrypt", "登录后访问业务 API"],
    ["FR-21", "Web 首页", "P0", "Vue3 导航、模块入口、数据概览", "未登录跳转登录页"],
    ["FR-22", "分析页图表", "P0", "ECharts 展示 MR 与 ADS 指标", "支持时间筛选"],
    ["FR-23", "预测页交互", "P0", "表单输入特征返回预测结果", "四项预测均可调用"],
    ["FR-24", "智能助手", "P1", "RAG + LLM 数据问答 SSE 流式", "POST /assistant/chat/stream"],
]


def _doc_meta_block(doc) -> None:
    """公众监督模板：文档信息 / 修订 / 审核 / 发行范围。"""
    add_h(doc, "文档信息", 1)
    add_table(
        doc,
        ["项目", "内容"],
        [
            ["项目名称", "新能源充电桩大数据分析项目"],
            ["产品名称", "CBP（Charging Bigdata Platform）"],
            ["文档类型", "见各文档封面标题"],
            ["编写单位", "项目组"],
            ["编写日期", "2026-06-22"],
            ["版本", "V1.3"],
        ],
    )
    add_h(doc, "文档审核记录", 2)
    add_table(
        doc,
        ["角色", "姓名", "日期", "签字"],
        [
            ["编写", "【请填写】", "2026-06-22", ""],
            ["审核", "【指导教师】", "2026-06-22", ""],
            ["批准", "【请填写】", "2026-06-22", ""],
        ],
    )
    add_h(doc, "文档发行范围", 2)
    add_p(
        doc,
        "本文档发行至项目组全体成员、指导教师及外部技术专家。"
        "未经编写单位书面许可，不得向项目外第三方扩散。",
    )


def _cover_block(doc, title: str, doc_no: str, version: str = "V1.3"):
    add_center_title(doc, "新能源充电桩大数据分析项目")
    add_center_title(doc, title)
    doc.add_paragraph()
    add_table(
        doc,
        ["项目", "内容"],
        [
            ["项目名称", "新能源充电桩大数据分析项目"],
            ["产品名称", "CBP（Charging Bigdata Platform）"],
            ["文档编号", doc_no],
            ["版本", version],
            ["编写日期", "2026-06-22"],
            ["数据库", "charging_bigdata"],
        ],
    )


def _revision_table(doc):
    add_h(doc, "文档修订记录", 2)
    add_table(
        doc,
        ["版本", "日期", "作者", "更改说明"],
        [
            ["V1.0", "2026-05-10", "项目组", "初稿：MR v1~v7 与 MySQL 落库"],
            ["V1.1", "2026-05-28", "项目组", "补充 Vue3 前端与 FastAPI 接口"],
            ["V1.2", "2026-06-08", "项目组", "增加 JWT 鉴权、ADS 五表、BI 对接"],
            ["V1.3", "2026-06-22", "项目组", "费用预测 XGBoost 选优；智能助手 RAG；Docker 云部署"],
        ],
    )


def _add_table_fields(doc, table_name: str):
    add_h(doc, table_name, 3)
    add_table(doc, FIELD_HEADERS, TABLE_FIELDS[table_name])


def build_srs_docx() -> int:
    doc = new_doc()
    _cover_block(doc, "软件需求规格说明书", "CBP-SRS-001")
    _doc_meta_block(doc)
    _revision_table(doc)

    add_h(doc, "第1章 引言", 1)
    add_h(doc, "1.1 编写目的", 2)
    add_p(
        doc,
        "本文档是新能源充电桩大数据分析项目（产品代号 CBP）的软件需求规格说明书（SRS），"
        "用于明确系统应具备的功能、性能、数据、接口、安全与完成标准。"
        "文档作为概要设计、详细设计、编码实现、系统测试、部署上线及交付确认的正式依据，"
        "确保项目组成员、指导教师与技术干系人对系统范围与质量要求达成一致理解。",
    )
    add_h(doc, "1.2 预期读者", 2)
    add_bullets(
        doc,
        [
            "项目经理与指导教师：把握范围、里程碑与质量口径；",
            "系统架构师与后端开发：依据接口与数据需求设计 FastAPI 服务层；",
            "前端开发：依据页面与交互需求实现 Vue3 + ECharts 展示；",
            "大数据开发：依据 MR 与 HDFS 需求实现 v1~v7 批处理与入库；",
            "数据分析与算法工程师：依据 ML 需求训练费用/时长/平台/SOC 四类模型；",
            "测试与运维人员：依据非功能与部署需求编写用例与运维手册；",
            "只读观摩用户：对照本文档核查功能完整性与文档规范性。",
        ],
    )
    add_h(doc, "1.3 文档约定", 2)
    add_p(
        doc,
        "本文档采用「应」「须」「可」等助动词描述需求优先级：「应/须」表示必须实现，「可」表示可选增强。"
        "需求编号以 FR-xx 表示功能需求、NFR-xx 表示非功能需求。"
        "图表占位处标注对应截图目录，定稿前由项目组插入实际界面或架构图。"
        "版本号遵循语义化：主版本变更表示范围调整，次版本表示功能增补。",
    )
    add_h(doc, "1.4 参考资料", 2)
    add_table(
        doc,
        ["序号", "文档/资源", "说明"],
        [
            ["1", "实践任务书与课时模块指南", "课程原始需求来源"],
            ["2", "charging-bigdata/README.md", "项目总览与快速启动"],
            ["3", "docs/需求规格说明书.md", "Markdown 版 SRS 对照"],
            ["4", "docs/概要设计说明书.md", "架构与模块划分"],
            ["5", "docs/数据库设计说明书.md", "表结构与约束"],
            ["6", "sql/schema.sql、ads_schema.sql、auth_schema.sql", "建表脚本"],
            ["7", "docker-compose.yml", "容器化部署定义"],
            ["8", "HDFS /Car/ 四个 CSV 数据集", "dsv13r1、dsv13r2、nvv2t、nvv2t_md"],
            ["9", "《新能源充电桩大数据项目》项目开发手册", "东软课程：数据准备/分布式存储/计算/分析/可视化五章"],
            ["10", "00.图表绘制规范/图表绘制与关系说明.md", "ER、时序、流程图绘制蓝本"],
        ],
    )
    add_h(doc, "1.5 编写背景", 2)
    add_p(
        doc,
        "东软在分布式新能源领域长期服务大型能源企业，本项目《新能源充电桩大数据项目》开发手册指出："
        "新能源汽车智能管理平台通过智能电网、物联网与互联网融合，实现充电用户便捷服务、"
        "充电桩与车用电池监管，并采用 Hadoop/MapReduce 对海量充电记录进行批处理分析，"
        "支持充电需求预测与充储电行为建模。手册定义从数据采集、分布式存储、分布式计算、"
        "数据分析挖掘到 BI 可视化的完整链路；本 CBP 系统在手册基线上实现全部核心指标，"
        "并扩展 FastAPI+Vue3 Web、JWT 鉴权、Docker 云部署与 RAG 智能助手。",
    )
    add_p(
        doc,
        "项目目标：建立高性能、高可靠充储电分析能力，通过对电池运行数据（dsv13r1/dsv13r2）"
        "与充电会话数据（nvv2t/nvv2t_md）的加工，为运营方提供电池状态监控、充电行为洞察、"
        "费用与时长预测及可视化决策支持，推动新能源汽车普及。",
    )

    add_h(doc, "第2章 项目概述", 1)
    add_h(doc, "2.1 背景", 2)
    add_p(
        doc,
        "系统面向充电桩运营场景，对电池状态 CSV 与充电行为 CSV 进行集中存储、批量计算、关系型持久化、"
        "可视化展示与智能预测。原始数据存放于 HDFS /Car/ 目录，经 MapReduce v1~v7 生成七类业务指标，"
        "由 load_mr_to_mysql.py 写入 MySQL charging_bigdata 库；"
        "Python 分析脚本进一步生成 ADS 汇总表与图表；"
        "四类机器学习模型（费用、时长、平台、SOC）由 train_all_models.py 训练并供 FastAPI 预测接口加载；"
        "Vue3 前端通过 Nginx 反代访问后端 REST API，实现登录鉴权、分析看板、预测表单与智能问答。",
    )
    add_h(doc, "2.2 功能性需求列表", 2)
    add_table(doc, ["编号", "功能名称", "优先级", "描述", "核查要点"], FUNCTIONAL_REQUIREMENTS)
    add_h(doc, "2.3 非功能性需求列表", 2)
    add_table(
        doc,
        ["编号", "类别", "需求描述", "指标"],
        [
            ["NFR-01", "性能", "BI 查询接口 P95 响应", "≤ 2s（有缓存）"],
            ["NFR-02", "性能", "预测接口单次推理", "≤ 500ms"],
            ["NFR-03", "性能", "MR 全量 v1~v7 批处理", "数据集规模内 ≤ 30min"],
            ["NFR-04", "可靠", "MySQL 入库幂等", "UPSERT 不重复"],
            ["NFR-05", "可靠", "Docker 健康检查", "mysqladmin ping 通过"],
            ["NFR-06", "安全", "密码存储", "bcrypt，禁止明文"],
            ["NFR-07", "安全", "API 鉴权", "Bearer JWT，业务路由需登录"],
            ["NFR-08", "安全", "CORS 白名单", "仅允许配置源"],
            ["NFR-09", "可维护", "分层架构", "api / services / repositories"],
            ["NFR-10", "可扩展", "MR 任务", "JobRunner 可增 v8+"],
            ["NFR-11", "可用", "Web 分辨率", "≥ 1280×720"],
            ["NFR-12", "兼容", "浏览器", "Chrome/Edge 最新版"],
        ],
    )
    add_h(doc, "2.4 约束", 2)
    add_bullets(
        doc,
        [
            "原始 CSV 禁止写入 Git，由用户上传至 HDFS /Car/；",
            "批处理须使用 Hadoop MapReduce（Java 8），不可仅用单机脚本替代 MR 统计；",
            "关系型数据库统一使用 MySQL 8.0，库名 charging_bigdata，字符集 utf8mb4；",
            "Web 后端采用 FastAPI，前端采用 Vue3 + TypeScript + Element Plus；",
            "云演示环境须通过 Docker Compose 一键启动，公网地址 http://115.29.194.137:8080；",
            "课程交付目标为三节点 Hadoop 分布式集群（非伪分布式）。",
        ],
    )
    add_h(doc, "2.5 用户角色", 2)
    add_table(
        doc,
        ["角色", "权限", "典型场景"],
        [
            ["系统管理员 admin", "用户管理、缓存清理、模型重载、RAG 重建", "运维与发布准备"],
            ["普通用户 user", "查看 BI、分析页、预测、智能助手", "日常运营查看"],
            ["数据分析师", "提交 MR、执行入库、训练模型", "离线数据处理"],
            ["只读观摩用户", "只读访问演示环境", "功能与文档核查"],
        ],
    )

    add_h(doc, "2.6 Web 前端子系统需求", 2)
    add_bullets(
        doc,
        [
            "技术栈：Vue3 + Vite + TypeScript + Pinia + Vue Router + Element Plus + ECharts；",
            "路由守卫：未登录访问业务页重定向 /login，Token 过期自动刷新或跳转登录；",
            "首页：展示系统简介、各模块入口卡片、关键指标摘要与 Datart BI 嵌入链接；",
            "登录/注册页：邮箱注册、邮件验证设密、忘记密码、双 Token 存储于 Pinia；",
            "分析页：按图表分区展示 MR 七指标与 ADS 五类分析，支持日期范围筛选与 ECharts 交互；",
            "预测页：费用/时长/平台/SOC 四个 Tab，表单校验后调用 /api/v1/predict/* 并展示结果；",
            "智能助手页：SSE 流式对话，展示引用片段与 Markdown 渲染；",
            "国际化：中英文切换（locale store）；",
            "构建：生产环境 Nginx 托管静态资源，/api 反代至 backend:8000。",
        ],
    )
    add_h(doc, "2.7 FastAPI 后端子系统需求", 2)
    add_bullets(
        doc,
        [
            "框架：FastAPI + Uvicorn，分层 api / services / repositories / models；",
            "认证模块 /auth：注册、登录、刷新、登出、邮件令牌、个人资料与 OTP 改密；",
            "BI 模块 /bi：电压电流、温度、SOC、充电次数、速率、热力图等只读统计，带查询缓存；",
            "预测模块 /predict：fee、duration、platform、soc 四个端点，加载 joblib/XGBoost 模型；",
            "视图配置 /views：图表元数据 CRUD，管理员可调整 BI 展示参数；",
            "智能助手 /assistant：RAG 检索 + LLM 流式回答，管理员可 /reindex；",
            "健康检查 /health、/health/ready：供 Docker 与负载均衡探活；",
            "安全：JWT Access 30min + Refresh 7d 轮换，密码 bcrypt，敏感配置走环境变量。",
        ],
    )
    add_h(doc, "2.8 MapReduce 批处理子系统需求", 2)
    add_bullets(
        doc,
        [
            "输入：HDFS /Car/dsv13r1.csv（无表头 11 列电池遥测）；",
            "公共组件：RecordParser、BatteryMapper、TimeKeyUtil、Avg2Reducer、JobBuilder、JobRunner；",
            "v1 V1VoltageCurrentHourly：小时键双指标均值 → /Car/output/v1/；",
            "v2 V2CellVoltageRange：小时键单体电压 max/min；",
            "v3 V3TemperatureTrend：时间点温度 max/min；",
            "v4 V4EnergyCapacityTrend：小时键能量容量均值；",
            "v5 V5ChargeCurrentStats：小时键电流 avg/max；",
            "v6 V6VoltageCurrentRelation：时间点电压电流；",
            "v7 V7SocTemperature：SOC 分段（10% 桶）温度均值；",
            "输出格式：key\\tmetric1\\tmetric2；入库脚本按唯一键 ON DUPLICATE KEY UPDATE。",
        ],
    )
    add_h(doc, "2.9 机器学习预测子系统需求", 2)
    add_bullets(
        doc,
        [
            "训练数据：nvv2t_md.csv（充电会话明细，含费用、时长、平台、SOC 等字段）；",
            "费用预测：LinearRegression 与 XGBoost 对比 RMSE，自动选优并序列化 fee_model.pkl；",
            "时长预测：回归模型预测充电时长（分钟）；",
            "平台预测：多分类模型预测充电平台类型；",
            "SOC 预测：回归模型预测目标 SOC；",
            "模型目录：analytics/output/models/，Docker 挂载只读；",
            "推理接口：FastAPI 加载模型，请求体 JSON 特征向量，响应含预测值与可选置信度；",
            "热更新：管理员 POST /predict/reload-models 重新加载磁盘模型。",
        ],
    )

    add_h(doc, "2.10 与东软开发手册章节对照", 2)
    add_p(doc, "下表将《项目开发手册》五章与本 CBP 实现一一对应，便于对照说明各阶段产出物。")
    add_table(
        doc,
        ["手册章/节", "手册内容", "CBP 实现"],
        [
            ["第一章 1.1", "项目背景、氢氪出行场景", "SRS 2.1 背景、首页说明"],
            ["第一章 1.2", "四数据集字段特征", "SRS 3.1 HDFS 文件表"],
            ["第二章 2.1~2.2", "HDFS Web UI 与常用命令", "部署手册 HDFS 命令节"],
            ["第二章 2.3", "业务数据上传 /Car/", "FR-01 数据准备"],
            ["第三章 3.3.1", "电压与充电流", "MR v1 → t_voltage_current"],
            ["第三章 3.3.2", "电池单体电压", "MR v2 → t_cell_voltage_range"],
            ["第三章 3.3.3", "时点高低温", "MR v3 → t_temperature"],
            ["第三章 3.3.4", "时点能量与容量", "MR v4 → t_energy_capacity"],
            ["第三章 3.3.5", "充电电流值", "MR v5 → t_charge_current_stats"],
            ["第三章 3.3.6", "组电压变化率/关系", "MR v6 → t_voltage_current_relation"],
            ["第三章 3.3.7", "电池状态与温度", "MR v7 → t_soc_temperature"],
            ["第四章 4.1", "日周月充电次数", "t_charging_daily/monthly、/charging"],
            ["第四章 4.2~4.3", "SOC 轨迹与热力图", "t_soc_hourly、/soc-heatmap"],
            ["第四章 4.5", "充电速度", "t_charge_rate_hourly、/charge-rate"],
            ["第四章 4.6", "性能分类指标", "/performance-report"],
            ["第四章 4.12~4.13", "费用预测 LR/XGB", "fee_model.pkl、/predict/fee"],
            ["第四章 4.16", "预测设备平台", "platform_model.pkl"],
            ["第五章 5.1", "Datart BI", "Datart 或 /mr-bi"],
            ["第五章 5.4.1~10", "自定义 Web 各页", "Vue3 对应路由全部实现"],
        ],
    )

    add_h(doc, "第3章 数据需求", 1)
    add_h(doc, "3.1 HDFS 原始文件", 2)
    add_table(
        doc,
        ["文件名", "路径", "用途", "使用模块"],
        [
            ["dsv13r1.csv", "/Car/", "电池遥测无表头 11 列", "MapReduce v1~v7"],
            ["dsv13r2.csv", "/Car/", "电池 SOC 时序", "Python SOC 分析、ADS"],
            ["nvv2t.csv", "/Car/", "充电会话记录", "充电次数/速率分析"],
            ["nvv2t_md.csv", "/Car/", "充电明细含费用", "ML 训练四模型"],
        ],
    )
    add_h(doc, "3.2 MySQL 逻辑表", 2)
    add_p(doc, "数据库 charging_bigdata 包含：7 张 MR 结果表、5 张 ADS 汇总表、4 张认证相关表及 3 个 BI 视图（v_voltage_current、v_temperature、v_soc_temperature）。")
    add_table(doc, ["表名", "类型", "来源", "说明"], ALL_TABLES_SUMMARY)
    add_h(doc, "3.3 关键字段说明", 2)
    add_p(
        doc,
        "MR 表以 record_hour（yyyyMMddHH）或 record_time（yyyyMMddHHmmss）或 soc_bucket 作为业务唯一键；"
        "ADS 表 time_key、record_date、record_month、hour_key 等与前端图表横轴对齐；"
        "sys_user 以 username/email 唯一标识，password_hash 仅存 bcrypt 摘要；"
        "所有浮点指标字段采用 DOUBLE，计数采用 INT，时间戳采用 DATETIME 或定长 VARCHAR 时间键。",
    )

    add_h(doc, "第4章 接口需求", 1)
    add_h(doc, "4.1 认证接口 /api/v1/auth", 2)
    add_bullets(
        doc,
        [
            "POST /register — 邮箱注册，发送验证邮件；",
            "POST /login — 返回 access_token + refresh_token；",
            "POST /refresh — 轮换 Refresh Token；",
            "POST /logout — 吊销 Refresh Token；",
            "GET /me — 当前用户信息；",
            "POST /forgot-password、/complete-email-token — 密码重置流程；",
            "PATCH /profile/password、/profile/username — 个人资料维护。",
        ],
    )
    add_h(doc, "4.2 BI 统计接口 /api/v1/bi", 2)
    add_bullets(
        doc,
        [
            "GET /bi/voltage-current、/cell-voltage、/temperature、/energy-capacity 等 MR 指标序列；",
            "GET /bi/charging-daily、/charging-monthly、/soc-hourly、/charge-rate、/soc-heatmap ADS 指标；",
            "POST /bi/cache/invalidate — 管理员清空缓存；",
            "均需 Authorization: Bearer <access_token>。",
        ],
    )
    add_h(doc, "4.3 预测接口 /api/v1/predict", 2)
    add_bullets(
        doc,
        [
            "POST /predict/fee — 充电费用预测；",
            "POST /predict/duration — 充电时长预测；",
            "POST /predict/platform — 充电平台分类；",
            "POST /predict/soc — 目标 SOC 预测；",
            "POST /predict/reload-models — 管理员热加载模型。",
        ],
    )
    add_h(doc, "4.4 其他接口", 2)
    add_bullets(
        doc,
        [
            "GET/POST /api/v1/views — BI 图表视图配置；",
            "POST /api/v1/assistant/chat/stream — 智能助手 SSE；",
            "GET /health、/health/ready — 健康探针；",
            "OpenAPI 文档：/docs（Swagger UI）。",
        ],
    )

    add_h(doc, "第5章 运行环境与部署", 1)
    add_h(doc, "5.1 三节点 Hadoop 集群", 2)
    add_table(
        doc,
        ["节点", "主机角色", "组件"],
        [
            ["节点 1 Master", "NameNode、ResourceManager", "MySQL、MapReduce 提交、可选 FastAPI"],
            ["节点 2 Slave", "DataNode、NodeManager", "存储与计算"],
            ["节点 3 Slave", "DataNode、NodeManager", "存储与计算"],
        ],
    )
    add_p(
        doc,
        "HDFS 副本数建议 3，WebHDFS 端口 9870，YARN Web UI 8088。"
        "分析节点通过 WebHDFS 读取 /Car/ 下 CSV，MR 作业通过 hadoop jar 提交。",
    )
    add_h(doc, "5.2 Docker 云演示环境", 2)
    add_p(
        doc,
        "阿里云 ECS（Ubuntu 22.04）使用 docker-compose 启动 mysql、backend、frontend 三服务。"
        "公网访问地址：http://115.29.194.137:8080 ；演示账号 admin@example.com / admin123。"
        "MySQL 容器自动执行 schema.sql、ads_schema.sql、auth_schema.sql 及种子数据脚本。"
        "前端 8080 映射 Nginx，反代 /api 至 backend:8000。",
    )
    add_bullets(
        doc,
        [
            "启动：docker compose up -d --build；",
            "环境变量：.env.docker 配置 MYSQL_ROOT_PASSWORD、JWT_SECRET、SMTP、LLM_API_KEY；",
            "模型与图表：挂载 analytics/output/models 只读进 backend 容器。",
        ],
    )

    add_h(doc, "第6章 页面与交互需求", 1)
    add_h(doc, "6.1 登录页", 2)
    add_p(
        doc,
        "居中卡片布局：顶部 CBP Logo 与项目名称，邮箱/密码输入框，「登录」「注册」「忘记密码」链接。"
        "登录成功写入 Pinia auth store 并跳转首页。错误提示使用 Element Plus Message 组件。",
    )
    add_placeholder_figure(doc, "图6-1 登录页", "登录表单、品牌区与错误提示截图")
    add_h(doc, "6.2 首页", 2)
    add_p(
        doc,
        "顶部导航栏含首页、分析、预测、助手、个人中心与退出。"
        "主体为栅格卡片：MR 批处理概览、BI 大屏入口、ML 预测入口、系统状态（健康检查）。"
        "底部展示版本号与部署环境标识。",
    )
    add_placeholder_figure(doc, "图6-2 首页", "模块入口卡片与导航栏")
    add_h(doc, "6.3 分析页", 2)
    add_p(
        doc,
        "左侧图表分类树（电压电流、温度、SOC、充电行为），右侧 ECharts 画布。"
        "顶部日期范围选择器与刷新按钮。图表支持缩放、数据点提示与图例切换。",
    )
    add_placeholder_figure(doc, "图6-3 分析页", "多图表分区与筛选器")
    add_h(doc, "6.4 预测页", 2)
    add_p(
        doc,
        "Tab 切换四项预测任务，每项对应独立表单（特征字段与单位提示）与「预测」按钮。"
        "结果区展示预测值、模型名称及可选特征重要性说明。",
    )
    add_placeholder_figure(doc, "图6-4 预测页", "费用预测表单与结果展示")

    expand_srs_mid_chapters(doc)

    add_h(doc, "第7章 非功能需求详述", 1)
    add_h(doc, "7.1 性能需求", 2)
    add_p(
        doc,
        "BI 查询对 MR/ADS 表执行聚合 SQL，后端实现内存缓存与 pipeline 完成后主动失效，"
        "保证演示时 P95 响应不超过 2 秒。预测接口仅做向量变换与模型推理，单次应在 500ms 内完成。"
        "MapReduce 七任务在课程数据集规模下总耗时不超过 30 分钟。"
        "前端路由懒加载与图表按需渲染，避免首屏加载过多 ECharts 实例。",
    )
    add_h(doc, "7.2 可靠性需求", 2)
    add_p(
        doc,
        "MySQL 入库采用唯一键 UPSERT，重复执行 load_mr_to_mysql.py 不产生脏数据。"
        "Docker Compose 为 mysql 配置 healthcheck，backend 依赖 mysql healthy 后启动。"
        "Refresh Token 服务端轮换，旧令牌吊销后不可复用。",
    )
    add_h(doc, "7.3 安全需求", 2)
    add_p(
        doc,
        "用户密码使用 bcrypt 哈希，cost factor 符合 passlib 默认安全级别。"
        "JWT Secret 通过环境变量注入，禁止硬编码进仓库。"
        "业务 API 除 /auth/login、/health 外均需 Bearer 认证。"
        "CORS 仅允许配置的 WEB 源。SMTP 与 LLM API Key 存放 .env.docker 不入 Git。",
    )
    add_h(doc, "7.4 可维护性需求", 2)
    add_p(
        doc,
        "后端遵循 api → services → repositories 分层，便于单元测试与替换数据源。"
        "MR 作业通过 JobRunner 统一调度，新增 v8 仅需增加 Job 类与表定义。"
        "SQL 迁移脚本按序号存放 sql/migrations/，Docker init 自动执行。",
    )
    add_h(doc, "7.5 可扩展性需求", 2)
    add_p(
        doc,
        "存储层可水平扩展 HDFS DataNode；计算层可增加 MR 或 Spark 任务；"
        "应用层 FastAPI 可无状态水平扩容，JWT 无状态校验；"
        "BI 可切换 Datart/DataEase；智能助手可替换 LLM 提供商与 Embedding 模型。",
    )
    expand_srs_ch7_extra(doc)
    expand_srs_late_chapters(doc)

    out = SUBMIT / "01.需求分析/06.需求规格说明书/新能源充电桩大数据分析项目-需求规格说明书.docx"
    return save_doc(doc, out)


def build_db_docx() -> int:
    doc = new_doc()
    _cover_block(doc, "数据库设计说明书", "CBP-DB-001", "V1.2")
    _revision_table(doc)

    add_h(doc, "1. 概述", 1)
    add_p(
        doc,
        "本文档描述新能源充电桩大数据分析项目 MySQL 数据库 charging_bigdata 的逻辑设计、"
        "表结构、字段定义、完整性约束及与 MapReduce、ADS、认证子系统的映射关系。"
        "原始 CSV 仅存 HDFS，不入关系库；MySQL 承载聚合结果、分析汇总与用户认证数据。",
    )

    add_h(doc, "1.3 数据库设计", 1)
    add_p(
        doc,
        "数据库采用 utf8mb4 字符集，InnoDB 存储引擎。"
        "命名规范：MR 结果表前缀 t_，ADS 表同前缀，认证表前缀 sys_。"
        "业务时间键统一使用定长 VARCHAR 格式字符串，便于与 MR 输出和前端图表对齐。",
    )

    add_h(doc, "1.3.1 E-R 图", 2)
    add_placeholder_figure(doc, "图1-1 数据库 E-R 图（MR+ADS）", "见 02.E-R图/MR与ADS逻辑E-R图.png")
    add_placeholder_figure(doc, "图1-2 认证模块 E-R 图", "见 02.E-R图/认证模块E-R图.png")
    add_p(
        doc,
        "绘制要求：须包含全部 18 个实体与 17 条关系连线（详见 00.图表绘制规范）。"
        "HDFS 四文件用虚线框表示逻辑源，MR 七表用实线箭头自 dsv13r1 聚合指向，"
        "ADS 五表用虚线自 dsv13r2/nvv2t 指向，认证四表以 sys_user 为中心 1:N 展开。",
    )
    add_table(
        doc,
        ["关系编号", "实体 A", "实体 B", "基数", "说明"],
        [
            ["R01", "HDFS dsv13r1", "t_voltage_current", "1:N", "v1 小时聚合"],
            ["R02", "HDFS dsv13r1", "t_cell_voltage_range", "1:N", "v2 单体电压"],
            ["R03", "HDFS dsv13r1", "t_temperature", "1:N", "v3 温度"],
            ["R04", "HDFS dsv13r1", "t_energy_capacity", "1:N", "v4 能量容量"],
            ["R05", "HDFS dsv13r1", "t_charge_current_stats", "1:N", "v5 电流"],
            ["R06", "HDFS dsv13r1", "t_voltage_current_relation", "1:N", "v6 关系"],
            ["R07", "HDFS dsv13r1", "t_soc_temperature", "1:N", "v7 SOC 温度"],
            ["R08", "HDFS dsv13r2", "t_soc_hourly", "1:N", "ADS SOC 折线"],
            ["R09", "HDFS nvv2t", "t_charging_daily", "1:N", "日充电次数"],
            ["R10", "HDFS nvv2t", "t_charging_monthly", "1:N", "月充电次数"],
            ["R11", "HDFS dsv13r2", "t_charge_rate_hourly", "1:N", "充电速率"],
            ["R12", "HDFS dsv13r2", "t_soc_heatmap", "1:N", "SOC 热力"],
            ["R13", "sys_user", "sys_refresh_token", "1:N", "双 Token"],
            ["R14", "sys_user", "sys_email_verification_token", "1:N", "邮件验证"],
            ["R15", "t_voltage_current", "v_voltage_current", "1:1", "BI 视图"],
            ["R16", "t_temperature", "v_temperature", "1:1", "BI 视图"],
            ["R17", "t_soc_temperature", "v_soc_temperature", "1:1", "BI 视图"],
        ],
    )
    add_p(doc, "本系统以「时间维度指标表」与「用户认证」两大域组织实体，MR 表之间无强外键，通过统一时间键在应用层关联展示。")

    add_h(doc, "1.3.2 数据库表总表", 2)
    add_table(doc, ["表名", "分类", "MR 任务", "用途说明"], ALL_TABLES_SUMMARY)

    add_h(doc, "1.3.3 各表字段定义", 2)
    for tbl in [
        "t_voltage_current",
        "t_cell_voltage_range",
        "t_temperature",
        "t_energy_capacity",
        "t_charge_current_stats",
        "t_voltage_current_relation",
        "t_soc_temperature",
        "sys_user",
        "t_soc_hourly",
        "t_charging_daily",
    ]:
        _add_table_fields(doc, tbl)

    add_p(
        doc,
        "其余 ADS 表 t_charging_monthly（record_month, charge_count）、"
        "t_charge_rate_hourly（hour_key, avg_rate）、"
        "t_soc_heatmap（record_day, hour_key, avg_soc）结构类似，均含 id 主键与业务唯一键。"
        "sys_refresh_token 含 username、token_hash、expires_at、revoked；"
        "sys_email_verification_token 含 user_id、purpose、token_hash、expires_at。",
    )

    add_h(doc, "1.3.4 完整性约束说明", 2)
    add_p(
        doc,
        "实体完整性：所有表均定义自增主键 id。"
        "参照完整性：认证表 user_id 逻辑关联 sys_user.id，由应用层保证，未建物理外键以便迁移灵活。"
        "用户定义完整性：MR 与 ADS 表对业务键建立 UNIQUE 约束，入库脚本依赖 ON DUPLICATE KEY UPDATE 实现幂等。"
        "域完整性：role 仅允许 admin/user；is_active、email_verified、revoked 为 0/1；"
        "浮点指标允许 NULL 表示该时间桶无数据。"
        "索引策略：业务唯一键建 UNIQUE INDEX，username、email、expires_at 等高频过滤列建普通索引以加速登录与令牌清理。",
    )
    add_bullets(
        doc,
        [
            "密码字段禁止明文，仅存储 bcrypt 哈希；",
            "Refresh Token 仅存 SHA256 摘要，不存原始令牌；",
            "邮件验证令牌过期后由定时任务或登录流程拒绝使用；",
            "BI 视图不含敏感字段，供 Datart 只读账号查询。",
        ],
    )

    out = SUBMIT / "02.系统设计/01.数据库设计/01.数据库设计文档/新能源充电桩大数据分析项目-数据库设计说明书.docx"
    return save_doc(doc, out)


def build_data_dict_docx() -> int:
    doc = new_doc()
    _cover_block(doc, "数据字典", "CBP-DD-001", "V1.2")

    add_h(doc, "1. 说明", 1)
    add_p(
        doc,
        "本数据字典对 charging_bigdata 库全部业务表、认证表字段进行统一说明，"
        "供开发、测试、数据分析及 BI 配置人员查阅。字段「空」列：否=NOT NULL，是=允许 NULL。"
        "键列：PK=主键，UK=唯一键，IDX=普通索引。"
        "正式提交格式为 Excel（.xls），文件：新能源充电桩大数据分析项目-数据字典.xls，"
        "结构对齐标准数据字典 xls 格式（DB一览表 + 每表一 Sheet）。",
    )

    add_h(doc, "2. MR 结果表数据字典", 1)
    for tbl in [
        "t_voltage_current",
        "t_cell_voltage_range",
        "t_temperature",
        "t_energy_capacity",
        "t_charge_current_stats",
        "t_voltage_current_relation",
        "t_soc_temperature",
    ]:
        add_h(doc, f"2.x {tbl}", 2)
        add_table(doc, FIELD_HEADERS, TABLE_FIELDS[tbl])

    add_h(doc, "3. ADS 汇总表数据字典", 1)
    add_h(doc, "3.1 t_soc_hourly", 2)
    add_table(doc, FIELD_HEADERS, TABLE_FIELDS["t_soc_hourly"])
    add_p(doc, "数据来源：analyze_soc.py 或 Spark load_ads_spark.py 从 dsv13r2.csv 按小时聚合平均 SOC，供分析页折线图与 /bi/soc-hourly 接口使用。")
    add_h(doc, "3.2 t_charging_daily", 2)
    add_table(doc, FIELD_HEADERS, TABLE_FIELDS["t_charging_daily"])
    add_p(doc, "数据来源：nvv2t.csv 按自然日统计充电会话次数，record_date 格式 yyyyMMdd，与前端日充电次数图表横轴一致。")
    add_h(doc, "3.3 t_charging_monthly", 2)
    add_table(doc, FIELD_HEADERS, TABLE_FIELDS["t_charging_monthly"])
    add_p(doc, "数据来源：nvv2t.csv 按自然月聚合充电次数，record_month 格式 yyyyMM。")
    add_h(doc, "3.4 t_charge_rate_hourly", 2)
    add_table(doc, FIELD_HEADERS, TABLE_FIELDS["t_charge_rate_hourly"])
    add_h(doc, "3.5 t_soc_heatmap", 2)
    add_table(doc, FIELD_HEADERS, TABLE_FIELDS["t_soc_heatmap"])

    add_h(doc, "3.6 BI 视图数据字典", 2)
    add_table(
        doc,
        ["视图名", "基表", "字段", "说明"],
        [
            ["v_voltage_current", "t_voltage_current", "record_hour, avg_pack_voltage, avg_charge_current", "电压电流趋势"],
            ["v_temperature", "t_temperature", "record_time, max_temperature, min_temperature", "温度双折线"],
            ["v_soc_temperature", "t_soc_temperature", "soc_bucket, avg_max_temperature, avg_min_temperature", "SOC 温度柱状"],
        ],
    )

    add_h(doc, "4. 认证表数据字典", 1)
    add_h(doc, "4.1 sys_user", 2)
    add_table(doc, FIELD_HEADERS, TABLE_FIELDS["sys_user"])
    add_h(doc, "4.2 sys_refresh_token", 2)
    add_table(doc, FIELD_HEADERS, TABLE_FIELDS["sys_refresh_token"])
    add_h(doc, "4.3 sys_token_blacklist", 2)
    add_table(doc, FIELD_HEADERS, TABLE_FIELDS["sys_token_blacklist"])
    add_h(doc, "4.4 sys_email_verification_token", 2)
    add_table(doc, FIELD_HEADERS, TABLE_FIELDS["sys_email_verification_token"])
    add_h(doc, "4.5 sys_profile_otp", 2)
    add_table(doc, FIELD_HEADERS, TABLE_FIELDS["sys_profile_otp"])
    add_h(doc, "4.6 bi_chart_view", 2)
    add_table(doc, FIELD_HEADERS, TABLE_FIELDS["bi_chart_view"])

    add_h(doc, "5. 代码表与枚举", 1)
    add_table(
        doc,
        ["字段", "取值", "含义"],
        [
            ["sys_user.role", "admin", "系统管理员"],
            ["sys_user.role", "user", "普通用户"],
            ["sys_user.is_active", "1", "账号启用"],
            ["sys_user.is_active", "0", "账号禁用"],
            ["soc_bucket", "0-10, 10-20, …", "SOC 十分位分段"],
            ["purpose", "verify_email", "注册邮箱验证"],
            ["purpose", "reset_password", "忘记密码重置"],
        ],
    )

    add_h(doc, "6. 字段命名与数据类型约定", 1)
    add_p(
        doc,
        "时间键字段统一采用定长字符串而非 DATETIME，以便与 MapReduce 输出 key 及 HDFS 原始 CSV 时间字段格式保持一致，"
        "减少入库与出图时的格式转换开销。record_hour 为 10 位 yyyyMMddHH；record_time 为 14 位 yyyyMMddHHmmss；"
        "record_date 为 8 位 yyyyMMdd；hour_key 为 2 位 HH。所有度量字段使用 DOUBLE 存储浮点指标，"
        "计数类使用 INT。主键 id 均为自增整数，业务唯一性由 UNIQUE 约束保证。",
    )
    add_bullets(
        doc,
        [
            "MR 表由 load_mr_to_mysql.py 写入，列顺序与 part-r-00000 输出一致；",
            "ADS 表由 analytics 或 Spark ETL 写入，写入前清空或 UPSERT；",
            "认证表由 FastAPI 应用层维护，禁止手工插入明文密码；",
            "Datart 等 BI 工具建议使用只读账号，仅授予 SELECT 权限。",
        ],
    )

    add_h(doc, "7. 表与 MapReduce 任务对照", 1)
    add_table(
        doc,
        ["表名", "MR 类", "输出路径", "Reducer 类型"],
        [
            ["t_voltage_current", "V1VoltageCurrentHourly", "/Car/output/v1", "Avg2Reducer"],
            ["t_cell_voltage_range", "V2CellVoltageRange", "/Car/output/v2", "MaxMinReducer"],
            ["t_temperature", "V3TemperatureTrend", "/Car/output/v3", "MaxMinReducer"],
            ["t_energy_capacity", "V4EnergyCapacityTrend", "/Car/output/v4", "Avg2Reducer"],
            ["t_charge_current_stats", "V5ChargeCurrentStats", "/Car/output/v5", "AvgMaxReducer"],
            ["t_voltage_current_relation", "V6VoltageCurrentRelation", "/Car/output/v6", "Avg2Reducer"],
            ["t_soc_temperature", "V7SocTemperature", "/Car/output/v7", "Avg2Reducer"],
        ],
    )

    out = SUBMIT / "02.系统设计/01.数据库设计/03.数据字典/新能源充电桩大数据分析项目-数据字典.docx"
    return save_doc(doc, out)


def build_outline_docx() -> int:
    doc = new_doc()
    _cover_block(doc, "概要设计说明书", "CBP-HLD-001", "V1.1")
    _doc_meta_block(doc)
    _revision_table(doc)

    add_h(doc, "第1章 引言", 1)
    add_h(doc, "1.1 编写目的", 2)
    add_p(
        doc,
        "本文档从系统总体层面描述新能源充电桩大数据分析项目的架构设计、功能模块划分、"
        "技术选型、部署结构、业务流程及页面布局，作为详细设计、编码实现、测试与交付的统一依据。",
    )
    add_h(doc, "1.2 背景", 2)
    add_p(
        doc,
        "新能源汽车充电产生大量电池运行与充电会话数据。本项目构建 HDFS → MapReduce → MySQL → BI/Web → ML 完整链路，"
        "在课程要求的三层以上大数据架构基础上，实现可运行的 CBP 平台。",
    )
    add_h(doc, "1.3 术语", 2)
    add_table(
        doc,
        ["术语", "说明"],
        [
            ["CBP", "Charging Bigdata Platform 产品代号"],
            ["MR", "MapReduce 批处理作业 v1~v7"],
            ["ADS", "应用数据服务层汇总表"],
            ["JWT", "JSON Web Token 双令牌鉴权"],
        ],
    )

    add_h(doc, "第2章 项目概述", 1)
    add_h(doc, "2.1 建设背景", 2)
    add_p(
        doc,
        "运营方需实时监控电池电气与热状态、分析充电行为规律、预测充电费用，"
        "并通过 Web 与 BI 统一展示。系统以 dsv13r1 等四个 CSV 为数据源，"
        "经分布式批处理与 Python 分析，输出七类 MR 指标、五类 ADS 汇总及四类 ML 预测能力。",
    )
    add_h(doc, "2.2 功能列表", 2)
    add_table(
        doc,
        ["序号", "功能模块", "说明"],
        [[str(i + 1), r[1], r[3]] for i, r in enumerate(FUNCTIONAL_REQUIREMENTS[:22])],
    )
    add_h(doc, "2.3 非功能需求", 2)
    add_bullets(
        doc,
        [
            "性能：BI P95≤2s，预测≤500ms；",
            "安全：JWT+bcrypt，API 鉴权；",
            "可靠：入库幂等、Docker 健康检查；",
            "可维护：分层架构与 SQL 迁移；",
            "可扩展：MR JobRunner、LLM 可替换。",
        ],
    )
    add_h(doc, "2.4 约束", 2)
    add_p(doc, "原始 CSV 不入 Git；批处理须用 MapReduce；Web 栈为 FastAPI+Vue3；演示地址 http://115.29.194.137:8080。")

    add_h(doc, "第3章 项目总体设计", 1)
    add_h(doc, "3.1 架构风格", 2)
    add_p(doc, "系统采用 B/S 架构，浏览器访问 Vue3 静态站，经 Nginx 反代调用 FastAPI REST 服务，后端访问 MySQL charging_bigdata。")
    add_h(doc, "3.2 运行环境", 2)
    add_table(
        doc,
        ["层次", "技术", "版本"],
        [
            ["存储", "Hadoop HDFS", "3.1.x"],
            ["计算", "MapReduce Java", "JDK 1.8"],
            ["数据库", "MySQL", "8.0"],
            ["后端", "FastAPI + Uvicorn", "Python 3.11"],
            ["前端", "Vue3 + TS + ECharts", "Node 18+"],
            ["ML", "scikit-learn + XGBoost", "joblib 序列化"],
            ["部署", "Docker Compose", "阿里云 ECS"],
        ],
    )
    add_h(doc, "3.3 系统总体设计", 2)
    add_p(
        doc,
        "逻辑上分为五层：展示层（Vue3、Datart BI）→ 应用层（FastAPI）→ 分析层（Python ML/ETL）→ "
        "计算层（MapReduce + 入库脚本）→ 存储层（HDFS 原始 + MySQL 结果）。"
        "各层通过明确接口解耦：MR 输出 part-r-00000 文本，入库脚本解析 TAB 分隔写入 MySQL；"
        "FastAPI repositories 封装 SQL，services 实现缓存与业务规则；"
        "前端 api 模块统一 axios 拦截器附加 JWT。",
    )
    add_p(
        doc,
        "认证子系统横切各业务模块：auth router 签发双 Token，bi/predict/views/assistant 路由依赖 get_current_user。"
        "智能助手通过 RAG 索引项目文档与表结构，SSE 流式返回 LLM 回答。",
    )
    add_placeholder_figure(doc, "图3-1 系统总体架构图", "见 01.需求分析/01.功能图/ 系统架构图")
    add_placeholder_figure(doc, "图3-2 数据流转图", "CSV→HDFS→MR→MySQL→API→前端")

    add_h(doc, "4 功能模块业务流程与时序", 1)
    add_p(
        doc,
        "以下对各核心功能模块的时序交互、关键类与接口实现思路进行说明。"
        "时序图源文件见 02.系统设计/02.时序图/ 目录，定稿前导出 PNG 插入本文档对应图号位置。",
    )
    expand_outline_ch4(doc)

    add_h(doc, "第5章 实体关系图说明", 1)
    add_p(
        doc,
        "MR 七表以时间或 SOC 桶为粒度相互独立，在 Dashboard 通过时间轴联动展示。"
        "ADS 五表由离线 ETL 从 HDFS 明细聚合，与 MR 表互补。"
        "认证域 sys_user 为中心，关联 refresh_token 与 email_verification_token。",
    )
    add_table(
        doc,
        ["实体组", "核心键", "说明"],
        [
            ["电池指标", "record_hour / record_time", "v1~v6 时序"],
            ["SOC 温度", "soc_bucket", "v7 分段"],
            ["充电行为", "record_date / month", "ADS 统计"],
            ["用户", "username / email", "认证与授权"],
        ],
    )

    expand_outline_ch5(doc)

    add_h(doc, "第6章 页面布局设计说明", 1)
    add_h(doc, "6.1 首页布局", 2)
    add_p(
        doc,
        "采用上-中-下结构：顶栏固定导航高度 56px，含 Logo、菜单、用户下拉；"
        "中部 24 栅格卡片 3 列排列模块入口；底部 Footer 显示版权与版本。"
        "主色调用 Element Plus 默认蓝，强调色用于预测与助手入口。",
    )
    add_h(doc, "6.2 登录页布局", 2)
    add_p(doc, "全屏居中，背景浅色渐变，表单宽度 400px，含邮箱、密码、验证码（注册）输入项。")
    add_h(doc, "6.3 分析页布局", 2)
    add_p(
        doc,
        "左侧 240px 侧边栏图表分类，右侧自适应 ECharts 区域，顶部工具条含日期选择与导出。"
        "多图表垂直堆叠，每块最小高度 320px，支持响应式收缩。",
    )
    add_h(doc, "6.4 预测页布局", 2)
    add_p(doc, "顶部 Tab 四项预测，左侧表单右侧结果，移动端改为上下堆叠。")
    add_h(doc, "6.5 智能助手页布局", 2)
    add_p(
        doc,
        "对话区占满主内容宽度，底部固定输入框与发送按钮。消息气泡区分用户与助手，"
        "助手消息支持 Markdown 与代码块渲染，流式输出时显示光标动画。",
    )
    add_placeholder_figure(doc, "图6-5 智能助手页", "对话气泡与输入区")
    expand_outline_ch6(doc)

    add_h(doc, "第7章 非功能性设计说明", 1)
    expand_outline_ch7(doc)

    add_h(doc, "第8章 技术选型与部署", 1)
    add_h(doc, "8.1 Docker Compose 服务", 2)
    add_table(
        doc,
        ["服务", "镜像/构建", "端口", "说明"],
        [
            ["mysql", "mysql:8.0", "3306 内部", "自动 init SQL"],
            ["backend", "backend/Dockerfile", "8000 内部", "FastAPI"],
            ["frontend", "frontend Dockerfile", "8080 对外", "Nginx 静态+反代"],
        ],
    )
    add_h(doc, "8.2 部署步骤摘要", 2)
    add_bullets(
        doc,
        [
            "克隆 charging-bigdata 至服务器；",
            "配置 .env.docker（JWT、MySQL、SMTP、LLM）；",
            "docker compose up -d --build；",
            "访问 http://115.29.194.137:8080 验证；",
            "Hadoop 集群单独部署，WebHDFS 供 ETL 读取。",
        ],
    )

    add_h(doc, "第9章 MapReduce 子系统概要设计", 1)
    add_h(doc, "9.1 任务总览", 2)
    add_table(
        doc,
        ["编号", "类名", "输入字段", "聚合键", "输出表"],
        [
            ["v1", "V1VoltageCurrentHourly", "pack_voltage, charge_current", "小时", "t_voltage_current"],
            ["v2", "V2CellVoltageRange", "max/min_cell_voltage", "小时", "t_cell_voltage_range"],
            ["v3", "V3TemperatureTrend", "max/min_temperature", "时间点", "t_temperature"],
            ["v4", "V4EnergyCapacityTrend", "energy, capacity", "小时", "t_energy_capacity"],
            ["v5", "V5ChargeCurrentStats", "charge_current", "小时", "t_charge_current_stats"],
            ["v6", "V6VoltageCurrentRelation", "voltage, current", "时间点", "t_voltage_current_relation"],
            ["v7", "V7SocTemperature", "SOC, 温度", "SOC 分段", "t_soc_temperature"],
        ],
    )
    add_h(doc, "9.2 公共组件", 2)
    add_bullets(
        doc,
        [
            "RecordParser / FieldIndex：解析 dsv13r1 无表头 11 列；",
            "BatteryMapper：统一校验、坏记录 Counter；",
            "TimeKeyUtil：小时键、时间点键、SOC 十分位桶；",
            "Avg2Reducer、MaxMinReducer、AvgMaxReducer：可复用聚合；",
            "JobBuilder：输出目录清理、Job 配置；",
            "JobRunner：顺序执行 v1~v7。",
        ],
    )
    add_p(
        doc,
        "输出格式为 key\\tmetric1\\tmetric2 的文本文件，存放于 HDFS /Car/output/vN/part-r-00000。"
        "入库脚本按 TAB 分隔解析，映射至 MySQL 对应列并执行 UPSERT。",
    )

    add_h(doc, "第10章 数据分析与机器学习概要设计", 1)
    add_h(doc, "10.1 Python 分析任务", 2)
    add_table(
        doc,
        ["任务", "脚本", "数据源", "输出"],
        [
            ["SOC 趋势", "analyze_soc.py", "dsv13r2.csv", "t_soc_hourly / soc_hourly.png"],
            ["日充电次数", "analyze_charging.py", "nvv2t.csv", "t_charging_daily"],
            ["月充电次数", "analyze_charging.py", "nvv2t.csv", "t_charging_monthly"],
            ["充电速率", "analyze_charging.py", "nvv2t.csv", "t_charge_rate_hourly"],
            ["SOC 热力图", "fix_ads_axes.py 等", "dsv13r2.csv", "t_soc_heatmap"],
        ],
    )
    add_h(doc, "10.2 机器学习模型", 2)
    add_p(
        doc,
        "train_all_models.py 基于 nvv2t_md.csv 训练四类模型：费用（LinearRegression vs XGBoost 选优）、"
        "时长回归、平台分类、SOC 回归。特征工程包括类别编码与数值归一化，"
        "模型序列化至 analytics/output/models/*.pkl，由 predict_service 加载推理。",
    )

    add_h(doc, "第11章 安全与运维设计", 1)
    add_p(
        doc,
        "认证采用 JWT 双 Token：Access Token 短期有效用于 API 调用，Refresh Token 长期有效存于 sys_refresh_token 表并支持轮换吊销。"
        "密码使用 bcrypt 哈希，邮件验证与重置密码通过 sys_email_verification_token 管理。"
        "敏感配置（JWT_SECRET、SMTP、LLM_API_KEY）通过 .env.docker 注入，不入版本库。",
    )
    add_bullets(
        doc,
        [
            "业务 API 默认需 Bearer 认证，/health 与登录注册接口除外；",
            "管理员接口（缓存清理、模型重载、RAG 重建）校验 role=admin；",
            "CORS 白名单限制前端来源；",
            "Docker healthcheck 保证 mysql 就绪后启动 backend；",
            "BI 查询缓存可在 ETL 完成后通过 /bi/cache/invalidate-pipeline 主动失效。",
        ],
    )

    add_h(doc, "第12章 源码目录结构", 1)
    add_table(
        doc,
        ["目录", "说明"],
        [
            ["mapreduce/", "Java MR v1~v7 源码与 pom.xml"],
            ["analytics/", "Python 分析、ETL、ML 训练脚本"],
            ["backend/", "FastAPI 应用 api/services/repositories"],
            ["frontend/", "Vue3 前端源码与 Nginx 配置"],
            ["sql/", "schema.sql、ads_schema.sql、auth_schema.sql、迁移与种子"],
            ["docker/", "MySQL init、Datart 配置"],
            ["scripts/", "部署、流水线、文档生成脚本"],
        ],
    )

    add_h(doc, "第13章 数据流与模块协作", 1)
    add_p(
        doc,
        "原始 CSV 由运维上传 HDFS /Car/ 后，MapReduce JobRunner 读取 dsv13r1 顺序产出七路聚合结果；"
        "load_mr_to_mysql.py 将 part-r-00000 解析入库 charging_bigdata 七张 MR 表；"
        "与此同时 analytics 脚本读取 dsv13r2 与 nvv2t 生成 ADS 五表及 PNG 图表；"
        "train_all_models.py 读取 nvv2t_md 训练四个 ML 模型；"
        "FastAPI 启动时加载模型文件，BI repository 连接 MySQL 只读查询；"
        "Vue3 前端通过 axios 调用 /bi 与 /predict，ECharts 绑定 JSON 序列化后的时序数据。",
    )
    add_p(
        doc,
        "智能助手子系统独立于批处理链路：indexer 扫描 docs 与 sql 目录构建向量索引，"
        "用户提问时 assistant_service 检索 Top-K 文档片段，拼接 Prompt 调用 DeepSeek API，"
        "以 SSE 流式返回至前端 AssistantView。该模块不依赖 HDFS 实时数据，但可回答表结构与 API 说明类问题。",
    )

    add_h(doc, "第14章 接口与前端协作说明", 1)
    add_table(
        doc,
        ["前端页面", "主要 API", "数据表"],
        [
            ["分析页-电压", "GET /bi/voltage-current", "t_voltage_current"],
            ["分析页-温度", "GET /bi/temperature", "t_temperature"],
            ["分析页-SOC", "GET /bi/soc-hourly", "t_soc_hourly"],
            ["分析页-充电", "GET /bi/charging-daily", "t_charging_daily"],
            ["预测页", "POST /predict/*", "models/*.pkl"],
            ["助手页", "POST /assistant/chat/stream", "chroma_db"],
        ],
    )
    add_p(
        doc,
        "前端 request.ts 统一配置 baseURL 为 /api/v1，请求拦截器从 Pinia auth store 读取 access_token 附加 Authorization 头；"
        "响应拦截器在 401 时尝试 refresh，失败则清空状态跳转登录。"
        "分析页图表组件封装 ECharts option 构建逻辑，根据接口返回的 time_key 数组动态设置 xAxis。",
    )

    add_h(doc, "第15章 测试策略概要", 1)
    add_p(
        doc,
        "测试分为单元测试（Mapper/Reducer 样例行）、集成测试（入库脚本 + MySQL）、"
        "API 测试（Swagger / pytest）、端到端测试（浏览器登录到图表展示）四级。"
        "上线前执行 scripts/verify-pipeline.sh 自动检查 HDFS 文件数、MySQL 表行数下限、"
        "/health/ready 数据库连通性，作为发布门禁。",
    )
    add_p(
        doc,
        "性能测试关注 BI 接口在高频刷新下的缓存命中率与 MySQL 慢查询日志；"
        "安全测试覆盖未授权访问、SQL 注入参数化防护、JWT 过期与吊销场景。"
        "文档与代码版本通过 Git tag 与项目资料提交目录 Word 文档修订记录表保持一致。",
    )
    add_p(
        doc,
        "本项目交付确认以功能演示与文档完整性为主，概要设计说明书与需求规格说明书、"
        "数据库设计说明书交叉引用，确保架构描述与表结构、API 列表一致，便于读者快速定位实现依据。",
    )

    out = SUBMIT / "04.项目概要设计说明书/新能源充电桩大数据分析项目-概要设计说明书.docx"
    return save_doc(doc, out)


def build_deploy_manual_docx() -> int:
    doc = new_doc()
    _cover_block(doc, "项目部署手册", "CBP-DEPLOY-001", "V1.0")

    add_h(doc, "1. 概述", 1)
    add_p(
        doc,
        "本手册说明新能源充电桩大数据分析项目（CBP）在 Hadoop 三节点集群与 Docker 云环境两种场景下的部署步骤、"
        "配置项、验证方法及常见问题处理。目标读者为运维人员与系统运维负责人。",
    )

    add_h(doc, "2. 环境要求", 1)
    add_h(doc, "2.1 硬件与系统", 2)
    add_table(
        doc,
        ["场景", "CPU", "内存", "磁盘", "操作系统"],
        [
            ["Hadoop 节点", "4 核+", "8GB+", "100GB+", "CentOS 7 / Ubuntu 20.04+"],
            ["Docker 单机", "2 核+", "4GB+", "40GB+", "Ubuntu 22.04 LTS"],
        ],
    )
    add_h(doc, "2.2 软件依赖", 2)
    add_bullets(
        doc,
        [
            "Hadoop 3.1.x、JDK 1.8、Maven 3.6+（MR 编译）；",
            "Docker 24+、Docker Compose v2；",
            "可选：Node 18+（本地前端构建）、Python 3.11（本地训练）。",
        ],
    )

    add_h(doc, "3. Hadoop 三节点集群部署", 1)
    add_h(doc, "3.1 集群规划", 2)
    add_table(
        doc,
        ["节点", "IP 示例", "角色"],
        [
            ["master", "192.168.x.1", "NameNode, ResourceManager, MySQL"],
            ["slave1", "192.168.x.2", "DataNode, NodeManager"],
            ["slave2", "192.168.x.3", "DataNode, NodeManager"],
        ],
    )
    add_h(doc, "3.2 安装步骤", 2)
    add_bullets(
        doc,
        [
            "配置 /etc/hosts 与 SSH 免密；",
            "解压 Hadoop，编辑 core-site.xml、hdfs-site.xml、yarn-site.xml、workers；",
            "格式化 NameNode（仅首次）：hdfs namenode -format；",
            "start-dfs.sh && start-yarn.sh；",
            "验证：9870 NameNode UI、8088 YARN UI；",
            "创建目录：hdfs dfs -mkdir -p /Car；",
            "上传数据：hdfs dfs -put dsv13r1.csv dsv13r2.csv nvv2t.csv nvv2t_md.csv /Car/。",
        ],
    )
    add_h(doc, "3.3 MapReduce 作业部署", 2)
    add_p(doc, "在 mapreduce 目录执行 mvn package，生成 target/cbp-mr-*.jar。")
    add_bullets(
        doc,
        [
            "hadoop jar cbp-mr.jar com.cbp.mr.JobRunner /Car/dsv13r1.csv /Car/output；",
            "检查输出：hdfs dfs -ls /Car/output/v1 … v7；",
            "执行 analytics/scripts/load_mr_to_mysql.py 写入 MySQL。",
        ],
    )

    add_h(doc, "4. Docker Compose 云部署", 1)
    add_h(doc, "4.1 服务器信息", 2)
    add_p(doc, "演示环境：阿里云 ECS，公网 IP 115.29.194.137，Web 端口 8080，访问 http://115.29.194.137:8080。")
    add_h(doc, "4.2 部署流程", 2)
    add_bullets(
        doc,
        [
            "git clone 项目至 /opt/charging-bigdata；",
            "cp .env.docker.example .env.docker 并编辑；",
            "docker compose up -d --build；",
            "docker compose ps 确认三服务 healthy；",
            "浏览器访问 8080，使用 admin@example.com / admin123 登录。",
        ],
    )
    add_h(doc, "4.3 环境变量说明", 2)
    add_table(
        doc,
        ["变量", "说明", "示例"],
        [
            ["MYSQL_ROOT_PASSWORD", "MySQL root 密码", "charging123"],
            ["JWT_SECRET", "JWT 签名密钥", "随机长字符串"],
            ["CORS_ORIGINS", "允许的前端源", "http://115.29.194.137:8080"],
            ["APP_PUBLIC_URL", "邮件链接前缀", "http://115.29.194.137:8080"],
            ["LLM_API_KEY", "智能助手 API Key", "sk-***"],
            ["WEB_PORT", "宿主机映射端口", "8080"],
        ],
    )
    add_h(doc, "4.4 数据初始化", 2)
    add_p(
        doc,
        "MySQL 容器启动时自动执行 docker-entrypoint-initdb.d 下脚本："
        "01-schema.sql、02-ads.sql、04-auth.sql、05-view-config.sql、迁移脚本及 seed 数据。"
        "模型文件需预先置于 analytics/output/models/ 并挂载进 backend。",
    )

    add_h(doc, "5. MySQL 配置", 1)
    add_p(
        doc,
        "库名 charging_bigdata，字符集 utf8mb4。"
        "远程访问参考 docs/MySQL远程配置与建库.md，执行 allow_root_remote.sql 与 grant_etl_user.sql。"
        "ETL 用户使用专用账号，仅授予 charging_bigdata 读写权限。",
    )

    add_h(doc, "6. 前端与 Nginx", 1)
    add_p(
        doc,
        "frontend 镜像内置 Nginx，将 /api 反向代理至 backend:8000，静态资源缓存 JS/CSS。"
        "构建参数 VITE_DATART_BASE_URL 指向 BI 大屏地址（可选 8088）。",
    )

    add_h(doc, "7. 验证清单", 1)
    add_table(
        doc,
        ["检查项", "命令/操作", "预期"],
        [
            ["健康检查", "curl /api/v1/health", "200 OK"],
            ["登录", "POST /auth/login", "返回 token"],
            ["BI 数据", "分析页打开", "图表有数据"],
            ["预测", "预测页提交", "返回数值"],
            ["HDFS", "hdfs dfs -ls /Car", "4 个 CSV"],
        ],
    )

    add_h(doc, "8. 常见问题", 1)
    add_bullets(
        doc,
        [
            "MySQL 启动失败：检查端口占用与 MYSQL_ROOT_PASSWORD；",
            "后端连不上库：确认 depends_on mysql healthy；",
            "预测 503：检查 models 目录挂载与 pkl 文件；",
            "CORS 错误：CORS_ORIGINS 需含实际访问 URL；",
            "MR 失败：检查 YARN 日志与输入路径。",
        ],
    )

    add_h(doc, "9. 完整流水线部署", 1)
    add_p(
        doc,
        "生产级演示需按顺序执行：① HDFS 上传四 CSV；② mvn package 编译 MR JAR；"
        "③ hadoop jar JobRunner 执行 v1~v7；④ load_mr_to_mysql.py 入库；"
        "⑤ analytics 脚本生成 ADS 与图表；⑥ train_all_models.py 训练模型；"
        "⑦ docker compose 启动 Web 服务。scripts/run-pipeline.sh 可一键串联上述步骤（需配置 pipeline.env）。",
    )
    add_bullets(
        doc,
        [
            "verify-pipeline.sh：检查 HDFS、MySQL 表行数、API 健康；",
            "import_web_demo.ps1：Windows 下导入演示种子；",
            "package_web_demo.ps1：打包可交付 Web 演示包；",
            "reset-demo-users.sh：重置演示账号密码。",
        ],
    )

    add_h(doc, "10. Datart BI 部署（可选）", 1)
    add_p(
        doc,
        "若需独立 BI 大屏，可执行 scripts/setup-datart-bi.ps1 或参考 docs/Datart-BI大屏部署手册.md。"
        "Datart 连接 charging_bigdata 只读账号，导入 v_voltage_current 等视图制作 Dashboard。"
        "前端构建参数 VITE_DATART_BASE_URL 指向 Datart 服务地址（默认 8088）。",
    )

    add_h(doc, "11. 回滚与备份", 1)
    add_p(
        doc,
        "MySQL 数据卷 mysql_data 由 Docker 管理，备份可使用 docker exec mysqldump charging_bigdata。"
        "HDFS 数据需定期 distcp 或快照备份 /Car 目录。"
        "回滚 Web 服务：docker compose down && git checkout <tag> && docker compose up -d --build。"
        "模型文件备份 analytics/output/models/ 目录，避免重训耗时。",
    )

    add_h(doc, "12. 监控与日志", 1)
    add_table(
        doc,
        ["组件", "日志/监控位置", "说明"],
        [
            ["Hadoop", "YARN Web UI :8088", "MR 作业状态与 Container 日志"],
            ["FastAPI", "docker logs cbp-backend", "API 请求与异常栈"],
            ["Nginx", "docker logs cbp-frontend", "静态资源与反代访问"],
            ["MySQL", "docker logs cbp-mysql", "慢查询与连接错误"],
        ],
    )
    add_p(
        doc,
        "建议上线前执行 curl http://115.29.194.137:8080/api/v1/health/ready 确认数据库连通，"
        "并在浏览器无痕模式验证登录与图表加载，排除缓存干扰。",
    )

    add_h(doc, "13. 本地开发环境搭建", 1)
    add_p(
        doc,
        "开发人员可在 Windows 本机仅启动前后端进行 UI 调试，MySQL 使用 Docker 单容器或远程库。"
        "后端：cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload --port 8000。"
        "前端：cd frontend && npm install && npm run dev，Vite 代理 /api 至 localhost:8000。"
        "MR 与 HDFS 相关功能需连接课程集群，配置 HDFS_NN_HOST 与 WebHDFS 用户。",
    )
    add_bullets(
        doc,
        [
            "backend/.env.example 复制为 .env 填写 MySQL 与 JWT；",
            "无 Hadoop 时可用 sql/seed/charging_bigdata_data.sql 种子数据演示 BI；",
            "模型训练在 analytics 目录执行 python scripts/train_all_models.py；",
            "本地勿将大数据 CSV 提交进 Git。",
        ],
    )

    add_h(doc, "14. 安全加固建议", 1)
    add_p(
        doc,
        "公网演示环境务必修改默认 MYSQL_ROOT_PASSWORD 与 JWT_SECRET，禁用弱口令 admin123 或限制 IP 访问。"
        "生产环境 SMTP、LLM_API_KEY 仅通过环境变量注入，定期轮换 Refresh Token 清理过期行。"
        "MySQL 不对公网暴露 3306，仅 Docker 内部网络 backend 可访问。"
        "Nginx 可配置 HTTPS（Let's Encrypt）保护登录凭据传输。",
    )

    add_h(doc, "15. 版本升级与迁移", 1)
    add_p(
        doc,
        "升级应用版本时推荐流程：docker compose pull && docker compose up -d --build 重新构建镜像；"
        "若 SQL 结构变更，将新迁移脚本放入 sql/migrations/ 并挂载至 mysql init 或手动执行。"
        "MySQL 数据卷 mysql_data 持久化业务数据，升级前务必备份 mysqldump。"
        "模型文件变更后需重启 backend 或调用 /predict/reload-models。"
        "前端静态资源变更后仅重建 frontend 镜像即可，不影响数据库。",
    )
    add_table(
        doc,
        ["变更类型", "操作", "回滚"],
        [
            ["仅后端代码", "重建 backend 镜像", "回退镜像 tag"],
            ["仅前端", "重建 frontend 镜像", "回退镜像 tag"],
            ["SQL 迁移", "执行 migration 脚本", "恢复 mysqldump"],
            ["MR 逻辑", "重跑 JobRunner + 入库", "从备份恢复表"],
        ],
    )

    add_h(doc, "16. backend 与 frontend 镜像说明", 1)
    add_p(
        doc,
        "backend/Dockerfile 基于 python:3.11-slim，安装 requirements.txt 中 FastAPI、SQLAlchemy、"
        "passlib、python-jose、chromadb、scikit-learn 等依赖，WORKDIR /app，"
        "CMD uvicorn app.main:app --host 0.0.0.0 --port 8000。"
        "构建上下文为项目根目录以便 COPY analytics 与 sql 资源。",
    )
    add_p(
        doc,
        "frontend/Dockerfile 多阶段：node:18 阶段 npm ci && npm run build，"
        "nginx:alpine 阶段复制 dist 与 nginx.conf，监听 80 端口，"
        "location /api 反代 http://backend:8000/api。"
        "构建参数 VITE_DATART_BASE_URL 在 docker-compose build.args 注入。",
    )
    add_h(doc, "17. 端口与网络", 1)
    add_table(
        doc,
        ["服务", "容器端口", "宿主机端口", "说明"],
        [
            ["frontend", "80", "8080（WEB_PORT）", "对外 Web 入口"],
            ["backend", "8000", "不暴露", "仅 Docker 网络内"],
            ["mysql", "3306", "不暴露", "仅 Docker 网络内"],
            ["Hadoop NN UI", "9870", "集群防火墙", "WebHDFS 与监控"],
            ["YARN UI", "8088", "集群防火墙", "MR 作业监控"],
        ],
    )
    add_p(
        doc,
        "docker compose 默认创建 bridge 网络，三服务通过服务名 mysql、backend、frontend 互相解析。"
        "仅 frontend 的 8080 映射宿主机，减小攻击面。"
        "若需宿主机调试 backend，可临时在 compose 中增加 ports: 8000:8000 并注意 CORS_ORIGINS 包含 localhost。",
    )
    add_h(doc, "18. 发布前检查清单", 1)
    add_bullets(
        doc,
        [
            "确认 http://115.29.194.137:8080 可访问且 SSL 无混合内容告警；",
            "admin@example.com 可登录，分析页至少三张图有数据；",
            "四项预测均可返回数值；",
            "HDFS /Car/ 四文件与 MR 输出目录可展示（集群演示时）；",
            "项目资料提交目录六类 Word 文档齐全。",
        ],
    )

    out = SUBMIT / "03.项目源码/06.项目部署手册/新能源充电桩大数据分析项目-项目部署手册.docx"
    return save_doc(doc, out)


def build_training_report_docx() -> int:
    doc = new_doc()
    add_center_title(doc, "东软实训综合实训报告")
    add_center_title(doc, "新能源充电桩大数据分析项目")
    doc.add_paragraph()
    add_table(
        doc,
        ["项目", "内容"],
        [
            ["姓名", "【请填写姓名】"],
            ["学号", "【请填写学号】"],
            ["班级", "【请填写班级】"],
            ["指导教师", "【请填写】"],
            ["实训时间", "2026年5月—2026年6月"],
            ["项目名称", "新能源充电桩大数据分析项目（CBP）"],
        ],
    )

    add_h(doc, "一、实训目的", 1)
    add_p(
        doc,
        "本次东软实训旨在通过完整的大数据分析项目实践，使学生掌握 Hadoop 分布式存储与 MapReduce 批处理、"
        "关系型数据库设计、Python 数据分析与机器学习、Web 前后端分离开发及 Docker 容器化部署等核心技能。"
        "以新能源充电桩运营场景为载体，完成从原始 CSV 数据上传 HDFS、七项电池指标 MR 统计、"
        "MySQL 持久化、BI 可视化、四项 ML 预测到 Vue3+FastAPI 全栈展示的端到端链路，"
        "培养工程化文档编写、团队协作与技术表达能力。",
    )
    add_p(
        doc,
        "通过本项目，我们理解了大数据「存—算—管—用」分层架构，熟悉了 JWT 鉴权、REST API 设计、"
        "ECharts 交互图表及 RAG 智能助手等企业级扩展能力，为今后从事数据开发与全栈工程打下基础。",
    )
    add_h(doc, "1.1 实训周记摘要", 2)
    add_table(
        doc,
        ["周次", "主要工作", "成果"],
        [
            ["第1周", "需求分析、Hadoop 集群搭建、HDFS 上传", "集群可用、/Car/ 有四文件"],
            ["第2周", "MapReduce v1~v4 开发与测试", "t_voltage_current 等四表有数据"],
            ["第3周", "MR v5~v7、入库脚本、数据库设计", "七表落库、ER 图完成"],
            ["第4周", "Python 分析、ML 训练、ADS 写入", "五类图表、四模型 pkl"],
            ["第5周", "FastAPI 后端、JWT 鉴权", "API /docs 可调试"],
            ["第6周", "Vue3 前端、ECharts 分析页", "全页面联调通过"],
            ["第7周", "Docker 部署、阿里云上线", "115.29.194.137:8080 可访问"],
            ["第8周", "智能助手、文档整理、联调彩排", "RAG 可用、交付物齐备"],
        ],
    )

    add_h(doc, "二、实训环境", 1)
    add_h(doc, "2.1 开发环境", 2)
    add_table(
        doc,
        ["类别", "配置"],
        [
            ["操作系统", "Windows 11 开发机 + Ubuntu 22.04 服务器"],
            ["大数据", "Hadoop 3.1.x 三节点集群，HDFS /Car/"],
            ["数据库", "MySQL 8.0，库名 charging_bigdata"],
            ["后端", "Python 3.11，FastAPI，Uvicorn"],
            ["前端", "Node 18，Vue3，TypeScript，Vite"],
            ["机器学习", "scikit-learn，XGBoost，joblib"],
            ["部署", "Docker Compose，阿里云 115.29.194.137:8080"],
        ],
    )
    add_h(doc, "2.2 数据集", 2)
    add_p(
        doc,
        "实训使用四个 CSV：dsv13r1.csv（电池遥测）、dsv13r2.csv（SOC）、"
        "nvv2t.csv（充电会话）、nvv2t_md.csv（含费用明细）。"
        "数据存放于 F:\\项目2资料\\数据集\\，上传至 HDFS /Car/，不进入 Git 仓库。",
    )
    add_h(doc, "2.3 工具与 IDE", 2)
    add_bullets(
        doc,
        [
            "IntelliJ IDEA：MapReduce Java 开发与远程调试；",
            "PyCharm / VS Code：Python 分析与 FastAPI 后端；",
            "WebStorm / VS Code：Vue3 前端与 TypeScript；",
            "DataGrip / Navicat：MySQL charging_bigdata 库管理；",
            "Maven 3.8：编译打包 cbp-mr JAR；",
            "Docker Desktop / 服务器 Docker：容器化部署。",
        ],
    )
    add_h(doc, "2.4 集群与云环境", 2)
    add_p(
        doc,
        "课程要求三节点 Hadoop 集群：Master 承担 NameNode、ResourceManager 与 MySQL；"
        "两台 Slave 作为 DataNode 与 NodeManager 扩展存储与计算能力。"
        "现场演示使用阿里云 ECS Ubuntu 22.04，通过 Docker Compose 部署 mysql、backend、frontend，"
        "公网访问 http://115.29.194.137:8080，演示账号 admin@example.com / admin123。",
    )

    add_h(doc, "三、需求分析", 1)
    add_h(doc, "3.1 业务场景", 2)
    add_p(
        doc,
        "新能源汽车充电过程中，电池管理系统持续上报组电压、单体电压、电流、温度、SOC 等遥测数据，"
        "充电运营商同时记录每次充电会话的起止时间、电量、费用、平台等信息。"
        "运营方需要回答：电池热状态是否异常？哪些时段充电最密集？单次充电费用能否提前预估？"
        "本项目围绕上述问题，将原始 CSV 转化为可查询、可可视化、可预测的数据资产。",
    )
    add_h(doc, "3.2 功能需求梳理", 2)
    add_p(
        doc,
        "根据任务书与业务场景，我们编制了《需求规格说明书》，明确系统须实现 HDFS 四文件管理、"
        "MapReduce v1~v7 批处理、七张 MR 表与五张 ADS 表入库、Datart BI 看板、"
        "Python 五类分析图、费用/时长/平台/SOC 四项 ML 预测、"
        "FastAPI 后端 REST 接口、Vue3 前端全页面及 JWT 邮箱登录鉴权。",
    )
    add_table(
        doc,
        ["需求编号", "模块", "完成标准"],
        [
            ["FR-01", "HDFS 数据准备", "四 CSV 可列出可读"],
            ["FR-02~08", "MR v1~v7", "七表有数据"],
            ["FR-16~19", "ML 四项预测", "API 返回合理数值"],
            ["FR-20", "JWT 鉴权", "未登录 401"],
            ["FR-21~23", "Web 三页面", "图表与表单可用"],
            ["FR-24", "智能助手", "SSE 流式回答"],
        ],
    )
    add_h(doc, "3.3 非功能与约束", 2)
    add_p(
        doc,
        "非功能方面约定 BI 查询 P95≤2s、预测推理≤500ms、密码 bcrypt 存储、"
        "Docker 一键部署与三节点 Hadoop 交付目标。"
        "用户角色划分为系统管理员、数据分析师、运营管理员与只读观摩用户，"
        "各角色对 MR 任务、模型训练、图表查看与系统配置具有不同权限。"
        "约束条件包括：批处理必须使用 MapReduce、Web 后端采用 FastAPI、"
        "演示环境公网地址 http://115.29.194.137:8080、原始数据禁止入 Git。",
    )

    add_h(doc, "四、系统设计", 1)
    add_h(doc, "4.1 总体架构", 2)
    add_p(
        doc,
        "系统采用五层 B/S 架构：展示层 Vue3 与 Datart BI；应用层 FastAPI；"
        "分析层 Python ETL 与 ML；计算层 MapReduce 与 load_mr_to_mysql.py；"
        "存储层 HDFS 原始文件与 MySQL charging_bigdata。"
        "认证子系统横切业务 API，采用双 Token JWT 与 Refresh 轮换机制。",
    )
    add_p(
        doc,
        "各层之间通过文件格式、SQL 表与 REST JSON 契约解耦："
        "MR 输出 TAB 文本、入库脚本、BI SQL、API Pydantic 模型、前端 TypeScript 接口类型逐级转化，"
        "任一层替换技术栈（如 Spark 替代 MR）只要保持表结构不变即可最小化上层改动。",
    )
    add_h(doc, "4.2 数据库设计", 2)
    add_p(
        doc,
        "设计 7 张 MR 结果表（t_voltage_current 至 t_soc_temperature）、"
        "5 张 ADS 汇总表（t_soc_hourly、t_charging_daily 等）、"
        "认证表 sys_user、sys_refresh_token、sys_email_verification_token。"
        "MR 表以 record_hour、record_time 或 soc_bucket 为唯一业务键，入库采用 ON DUPLICATE KEY UPDATE。",
    )
    add_p(
        doc,
        "数据库命名与 charging-bigdata/sql/schema.sql、ads_schema.sql、auth_schema.sql 脚本完全一致，"
        "Docker 初始化与本地开发共用同一套 DDL，避免环境差异。"
        "BI 视图 v_voltage_current、v_temperature、v_soc_temperature 简化 Datart 数据源配置。",
    )
    add_h(doc, "4.3 接口设计", 2)
    add_p(
        doc,
        "REST API 按 /api/v1 分组：/auth 认证、/bi 统计、/predict 预测、"
        "/views 视图配置、/assistant 智能助手、/health 探活。"
        "业务接口需 Bearer JWT，OpenAPI 文档自动生成于 /docs。",
    )
    add_h(doc, "4.4 安全设计", 2)
    add_p(
        doc,
        "采用双 Token 机制：Access Token 短期（默认 30 分钟）用于 API 请求头，"
        "Refresh Token 长期（默认 7 天）存于 HttpOnly 策略的客户端存储并由服务端 sys_refresh_token 表轮换管理。"
        "密码注册与修改均走 bcrypt 哈希，邮件验证与忘记密码通过 sys_email_verification_token 一次性令牌完成。",
    )

    add_h(doc, "五、详细设计与实现", 1)
    add_h(doc, "5.1 MapReduce 实现", 2)
    add_p(
        doc,
        "在 mapreduce 模块实现 v1~v7 共七个 Java 作业。公共包 com.cbp.mr 提供 RecordParser 解析 dsv13r1 无表头 11 列、"
        "BatteryMapper 基类过滤坏行、TimeKeyUtil 生成小时键/时间点键/SOC 十分位桶、"
        "Avg2Reducer/MaxMinReducer 等可复用聚合器、JobBuilder 统一作业配置。"
        "v1 按小时平均 pack_voltage 与 charge_current；v2 统计单体电压 hourly max/min；"
        "v3 按时间点记录温度极值；v4 平均可用能量与容量；v5 充电电流 avg/max；"
        "v6 保留时间点电压电流对；v7 按 SOC 分段统计平均温度。"
        "JobRunner 顺序提交七作业，输出 TAB 分隔至 /Car/output/v1…v7/part-r-00000。",
    )
    add_p(
        doc,
        "以 v1 为例：Mapper 读取一行 CSV，RecordParser 按列索引取出时间戳、pack_voltage、charge_current，"
        "TimeKeyUtil.toHourKey 将时间戳截断为 yyyyMMddHH 作为 emit key，value 为两列数值拼接字符串；"
        "Reducer 端 Avg2Reducer 对同小时多条记录累加求平均，输出格式 hourKey\\tavgVoltage\\tavgCurrent。"
        "Combiner 与 Reducer 复用同一逻辑减少 Shuffle 数据量。"
        "作业提交前 JobBuilder 自动删除输出目录避免 FileAlreadyExistsException。",
    )
    add_p(
        doc,
        "v7 的 SOC 分段将 0~100% 按 10% 桶划分，Mapper 根据当前 SOC 值映射到如 30-40 桶名，"
        "同时携带 max_temperature 与 min_temperature，Reducer 计算桶内平均最高温与平均最低温，"
        "结果写入 t_soc_temperature 供分析页柱状图展示电池在不同电量状态下的热特性。",
    )
    add_p(
        doc,
        "入库脚本 load_mr_to_mysql.py 读取 HDFS 输出，解析 key 与指标列，"
        "批量 UPSERT 至 MySQL 对应表。重复执行不产生重复行，支持上线前数据刷新。",
    )
    add_h(doc, "5.1.1 各任务实现要点", 3)
    add_table(
        doc,
        ["任务", "Mapper 逻辑", "Reducer 逻辑", "难点"],
        [
            ["v1", "提取小时键与电压电流", "双字段求平均", "时间字段解析"],
            ["v2", "提取单体电压", "小时 max/min", "极值合并"],
            ["v3", "提取时间点温度", "时间点 max/min", "细粒度键"],
            ["v4", "提取能量容量", "双字段平均", "单位换算"],
            ["v5", "提取充电电流", "平均与最大", "AvgMaxReducer"],
            ["v6", "保留电压电流对", "时间点聚合", "关系散点数据量"],
            ["v7", "SOC 分段", "分段温度均值", "SOC 桶边界"],
        ],
    )
    add_h(doc, "5.2 Web 后端实现", 2)
    add_p(
        doc,
        "FastAPI 项目按 api/services/repositories 分层。auth_service 实现邮箱注册、"
        "邮件令牌验证、bcrypt 校验、双 Token 签发与 Refresh 轮换。"
        "bi_service 封装 MR/ADS 表 SQL 查询，内存缓存提升大屏响应。"
        "predict_service 加载 analytics/output/models 下四个 joblib/pkl 模型，"
        "提供 fee、duration、platform、soc 推理端点。"
        "assistant_service 集成 Chroma 向量库与 DeepSeek LLM，支持 SSE 流式问答。",
    )
    add_p(
        doc,
        "登录流程：用户 POST /auth/login 提交邮箱与密码，auth_service 查询 sys_user 表，"
        "passlib.verify 校验 password_hash，通过后 jwt_service 签发 access_token（含 sub、role、exp）"
        "与 refresh_token（随机串哈希存入 sys_refresh_token）。"
        "前端 axios 拦截器在 Header 附加 Bearer access_token，"
        "access 过期时自动 POST /auth/refresh 携带 refresh_token 换取新对，"
        "若 refresh 已吊销则跳转登录页。",
    )
    add_p(
        doc,
        "BI 查询示例：GET /bi/voltage-current 可选 start_hour、end_hour 查询参数，"
        "bi_repository 执行 SELECT record_hour, avg_pack_voltage, avg_charge_current "
        "FROM t_voltage_current WHERE record_hour BETWEEN :s AND :e ORDER BY record_hour，"
        "bi_service 将结果 JSON 化并写入进程内缓存字典，键为查询 SQL 哈希，"
        "管理员 POST /bi/cache/invalidate 可清空缓存以便 ETL 后刷新数据。",
    )
    add_h(doc, "5.2.1 后端模块说明", 3)
    add_bullets(
        doc,
        [
            "app/api/v1/endpoints/auth.py：注册、登录、刷新、邮件令牌、个人资料；",
            "app/api/v1/endpoints/bi.py：MR/ADS 统计查询与缓存管理；",
            "app/api/v1/endpoints/predict.py：四项 ML 推理与模型重载；",
            "app/api/v1/endpoints/assistant.py：RAG 问答 SSE 与索引重建；",
            "app/repositories/bi_repository.py：原生 SQL 与参数化查询；",
            "app/core/config.py：环境变量集中配置。",
        ],
    )
    add_h(doc, "5.3 Web 前端实现", 2)
    add_p(
        doc,
        "Vue3 + Vite 构建，Pinia 管理 auth 与 locale 状态，Vue Router 配置路由守卫。"
        "登录页支持邮箱注册与忘记密码；首页模块卡片导航；"
        "分析页 ECharts 展示电压电流、温度、SOC、充电次数、速率与热力图；"
        "预测页四个 Tab 表单调用 /predict API；助手页 SSE 渲染 Markdown 回答。"
        "axios 拦截器自动附加 JWT 与 401 刷新逻辑。生产构建由 Nginx 托管，/api 反代 backend。",
    )
    add_p(
        doc,
        "分析页 AnalysisView 在 onMounted 时并行请求多个 /bi 接口，"
        "将返回的时序数组映射为 ECharts line/bar/heatmap option。"
        "例如电压电流双轴折线图：xAxis 为 record_hour 格式化显示，"
        "series 两条分别为 avg_pack_voltage 与 avg_charge_current，"
        "tooltip 触发 axis 联动。SOC 热力图将 t_soc_heatmap 的 record_day 与 hour_key 转为二维矩阵，"
        "visualMap 组件映射 avg_soc 颜色梯度。",
    )
    add_p(
        doc,
        "预测页 PredictView 为四项任务分别定义 reactive 表单模型，"
        "字段标签与 placeholder 与训练特征列一致，提交前 Element Plus 表单校验非空与数值范围。"
        "提交后展示 loading 状态，成功则在结果卡片显示预测值与后端返回的 model_name。",
    )
    add_h(doc, "5.3.1 前端页面与路由", 3)
    add_table(
        doc,
        ["路由", "组件", "功能"],
        [
            ["/login", "LoginView", "邮箱登录与注册入口"],
            ["/", "HomeView", "模块导航与概览"],
            ["/analysis", "AnalysisView", "ECharts 多图表分析"],
            ["/predict", "PredictView", "四项 ML 预测表单"],
            ["/assistant", "AssistantView", "智能问答对话"],
            ["/profile", "ProfileView", "修改密码与昵称"],
        ],
    )
    add_h(doc, "5.4 机器学习实现", 2)
    add_p(
        doc,
        "基于 nvv2t_md.csv，train_all_models.py 训练四类模型："
        "费用预测对比 LinearRegression 与 XGBoost，按 RMSE 自动选优；"
        "时长回归、平台多分类、SOC 回归均做特征工程与 train/test 划分。"
        "模型序列化至 analytics/output/models/，Docker 挂载只读供 FastAPI 加载。"
        "现场演示可输入特征展示预测结果，管理员可热重载模型。",
    )
    add_p(
        doc,
        "特征工程阶段对类别列进行 LabelEncoder 或 OneHotEncoder，数值列缺失值填充中位数。"
        "训练集与测试集按 8:2 划分，回归任务以 RMSE/MAE 评估，分类任务以 accuracy 与 F1 评估。"
        "费用预测因 XGBoost 在非线性关系上优于线性回归，最终选优结果写入模型元数据，"
        "API 响应可告知用户当前使用的是 xgboost 还是 linear_regression 模型。",
    )
    add_h(doc, "5.4.1 模型训练细节", 3)
    add_p(
        doc,
        "费用预测模块 fee_models.py 对 LinearRegression 与 XGBoost 在同一训练集上比较 RMSE，"
        "将更优模型保存为 fee_model.pkl 并记录元数据供 API 返回 model_name。"
        "时长预测采用 GradientBoostingRegressor；平台预测采用 RandomForestClassifier；"
        "SOC 预测采用线性回归。所有模型经 StandardScaler 或 OneHotEncoder 预处理，"
        "训练脚本 train_all_models.py 一键输出四个 pkl 至 analytics/output/models/。",
    )
    add_h(doc, "5.5 智能助手与 BI", 2)
    add_p(
        doc,
        "RAG 索引器扫描项目文档与表结构，Embedding 使用 BAAI/bge-small-zh-v1.5，"
        "向量存储于 chroma_db。用户提问时检索 Top-K 片段拼接 Prompt，"
        "LLM 流式返回。Datart BI 连接 MySQL 只读账号，展示 MR 视图 v_voltage_current 等大屏。",
    )
    add_p(
        doc,
        "智能助手典型问答包括：「有哪些 MR 表」「费用预测用什么模型」「如何重新部署」等，"
        "索引范围覆盖 docs/、sql/ 注释与 README，管理员 POST /assistant/reindex 可在文档更新后重建向量库。"
        "BI 大屏通过 VITE_DATART_BASE_URL 嵌入首页 iframe 或新窗口打开，"
        "与 Vue 内置 ECharts 分析页形成「大屏+明细」双轨展示。",
    )
    add_h(doc, "5.6 Python 分析与 ETL", 2)
    add_p(
        doc,
        "analytics 目录下 hdfs_io.py 通过 WebHDFS 流式读取 HDFS 文件，避免整文件下载到本地。"
        "analyze_soc.py 按小时聚合 dsv13r2 的 SOC 写入 t_soc_hourly 并生成折线图；"
        "analyze_charging.py 统计 nvv2t 的日/月充电次数与小时充电速率；"
        "etl/mr_tasks.py 与 Spark 脚本 load_ads_spark.py 提供备选 ADS 写入路径。"
        "图表输出至 analytics/output/charts/，供文档插图与技术展示。",
    )
    add_h(doc, "5.7 Docker 部署实现", 2)
    add_p(
        doc,
        "docker-compose.yml 定义 mysql、backend、frontend 三服务。"
        "MySQL 通过 docker-entrypoint-initdb.d 自动执行 schema、ads、auth、迁移与种子脚本；"
        "backend Dockerfile 多阶段构建，安装 Python 依赖并复制应用代码；"
        "frontend 构建阶段 npm run build，运行阶段 Nginx 托管 dist 并反代 /api。"
        "最终在阿里云 115.29.194.137:8080 提供完整演示环境。",
    )
    add_h(doc, "5.8 HDFS 数据准备实践", 2)
    add_p(
        doc,
        "实训第一周完成 Hadoop 三节点集群搭建与 HDFS 目录初始化。"
        "在 Master 节点执行 hdfs dfs -mkdir -p /Car 创建业务目录，"
        "通过 scp 将 Windows 开发机 F:\\项目2资料\\数据集\\ 下四个 CSV 传至集群，"
        "再执行 hdfs dfs -put 上传至 /Car/。"
        "验证阶段使用 hdfs dfs -ls /Car 确认文件大小与副本数，"
        "hdfs dfs -cat /Car/dsv13r1.csv | head 抽样查看字段格式，"
        "确认无表头、逗号分隔、共 11 列与 RecordParser 定义一致。",
    )
    add_h(doc, "5.9 文档与规范", 2)
    add_p(
        doc,
        "项目组同步维护 Markdown 设计文档于 docs/ 目录，并通过 generate_submission_docs_full.py "
        "自动生成宋体 Word 版并纳入项目交付目录，符合项目文档编写规范。"
        "代码仓库 charging-bigdata 按 mapreduce、analytics、backend、frontend、sql 分模块，"
        "README 提供快速启动说明，docker/README.md 说明容器部署细节。",
    )

    add_h(doc, "六、测试", 1)
    add_h(doc, "6.1 功能测试", 2)
    add_table(
        doc,
        ["模块", "用例", "结果"],
        [
            ["HDFS", "上传 4 CSV，ls /Car", "通过"],
            ["MR", "JobRunner 七任务", "通过"],
            ["入库", "load_mr_to_mysql", "通过"],
            ["登录", "admin@example.com 登录", "通过"],
            ["BI API", "/bi/voltage-current", "通过"],
            ["预测", "四项 POST /predict", "通过"],
            ["助手", "SSE 流式问答", "通过"],
        ],
    )
    add_h(doc, "6.2 部署测试", 2)
    add_p(
        doc,
        "在阿里云 ECS 执行 docker compose up -d --build，"
        "验证 http://115.29.194.137:8080 可访问，健康检查 /health 返回 200，"
        "MySQL 种子数据加载完成，图表与预测功能正常。",
    )
    add_h(doc, "6.3 性能与安全测试", 2)
    add_p(
        doc,
        "使用浏览器开发者工具测量分析页首屏与 BI 接口响应时间，缓存命中后 P95 低于 2 秒。"
        "预测接口单次调用在本地模型加载后稳定在 500ms 以内。"
        "安全测试验证未带 Token 访问 /bi 返回 401、错误密码登录失败、"
        "Refresh Token 轮换后旧令牌无法刷新。",
    )
    add_h(doc, "6.4 问题与修复记录", 2)
    add_table(
        doc,
        ["问题", "原因", "解决方案"],
        [
            ["MR 作业 OOM", "Reducer 内存不足", "调整 yarn 内存参数"],
            ["WebHDFS 403", "用户权限", "HDFS_USER 配置为 hdfs"],
            ["CORS 拦截", "源未白名单", "CORS_ORIGINS 加入公网 URL"],
            ["预测 503", "模型未挂载", "Docker volume 挂载 models"],
            ["邮件发不出", "SMTP 未配置", "演示环境跳过或填 .env"],
        ],
    )
    add_h(doc, "6.5 测试结论", 2)
    add_p(
        doc,
        "综合功能、部署、性能与安全四类测试，新能源充电桩大数据分析项目满足需求规格说明书规定的完成标准："
        "MapReduce 七任务全部通过、MySQL 表数据完整、Web 全页面可用、四项预测接口正常、"
        "JWT 鉴权有效、Docker 云环境 http://115.29.194.137:8080 稳定运行。"
        "遗留项为邮件 SMTP 在部分网络环境下需额外配置，不影响核心演示路径。",
    )

    expand_training_late_chapters(doc)

    add_h(doc, "八、分工说明", 1)
    add_table(
        doc,
        ["成员", "学号", "主要负责模块"],
        [
            ["【成员甲】", "【学号】", "MapReduce v1~v4、HDFS 数据准备、部署文档"],
            ["【成员乙】", "【学号】", "MapReduce v5~v7、MySQL 入库、数据库设计"],
            ["【成员丙】", "【学号】", "FastAPI 后端、JWT 鉴权、BI API"],
            ["【成员丁】", "【学号】", "Vue3 前端、ECharts 分析页、预测页"],
            ["【成员戊】", "【学号】", "Python ML 训练、智能助手 RAG、实训报告统稿"],
        ],
    )
    add_p(doc, "注：请根据实际小组情况修改上表姓名、学号与分工。")

    add_h(doc, "九、致谢", 1)
    add_p(
        doc,
        "感谢东软实训指导教师在 Hadoop 集群组网、Docker 部署与文档规范方面的悉心指导；"
        "感谢小组成员在 MR 调试、前端联调与资料整理中的互相配合；"
        "感谢 Apache Hadoop、FastAPI、Vue.js、ECharts、scikit-learn 等开源社区提供的优秀工具。"
        "本报告与需求规格、概要设计、数据字典 xls 及 charging-bigdata 源码可交叉验证。",
    )

    add_h(doc, "十、附录", 1)
    add_h(doc, "9.1 项目交付物清单", 2)
    add_table(
        doc,
        ["类别", "交付物", "路径"],
        [
            ["文档", "需求规格说明书", "项目资料提交/01.需求分析/"],
            ["文档", "数据库设计说明书", "项目资料提交/02.系统设计/"],
            ["文档", "概要设计说明书", "项目资料提交/04.项目概要设计说明书/"],
            ["文档", "部署手册", "项目资料提交/03.项目源码/06.项目部署手册/"],
            ["源码", "charging-bigdata", "Git 仓库根目录"],
            ["数据", "HDFS /Car/ 四 CSV", "用户自行上传，不入库"],
            ["演示", "Docker 云环境", "http://115.29.194.137:8080"],
        ],
    )
    add_h(doc, "9.2 核心命令备忘", 2)
    add_bullets(
        doc,
        [
            "hdfs dfs -put 本地/*.csv /Car/ — 上传原始数据；",
            "mvn -f mapreduce/pom.xml package — 编译 MR JAR；",
            "hadoop jar cbp-mr.jar com.cbp.mr.JobRunner /Car/dsv13r1.csv /Car/output — 跑批；",
            "python analytics/scripts/load_mr_to_mysql.py — MR 结果入库；",
            "python analytics/scripts/train_all_models.py — 训练 ML 模型；",
            "docker compose up -d --build — 启动 Web 演示环境。",
        ],
    )
    add_h(doc, "9.3 参考文献", 2)
    add_bullets(
        doc,
        [
            "Apache Hadoop 官方文档 — MapReduce Tutorial；",
            "FastAPI 官方文档 — Security OAuth2 JWT；",
            "Vue.js 3 官方文档 — Pinia 状态管理；",
            "scikit-learn User Guide — Model persistence；",
            "东软实训课程讲义与任务书。",
        ],
    )
    add_h(doc, "9.4 系统演示建议流程", 2)
    add_p(
        doc,
        "建议现场演示按以下顺序进行，总时长约 15 分钟："
        "① 开场介绍项目背景与五层架构（1 分钟）；"
        "② 展示 HDFS /Car/ 四文件与 MR 输出目录（2 分钟）；"
        "③ 打开 MySQL 或 BI 展示七张 MR 表样例数据（2 分钟）；"
        "④ 浏览器访问 http://115.29.194.137:8080 登录系统（1 分钟）；"
        "⑤ 分析页演示电压、温度、SOC、充电次数图表联动（4 分钟）；"
        "⑥ 预测页现场输入特征演示费用与 SOC 预测（2 分钟）；"
        "⑦ 智能助手提问「充电大数据有哪些表」展示 RAG（2 分钟）；"
        "⑧ 总结技术亮点与小组分工（1 分钟）。",
    )
    add_p(
        doc,
        "演示前一日务必在目标环境全量跑通 pipeline，确认种子用户可登录、图表有数据、模型文件已挂载。"
        "准备备用截图与离线视频，防止公网或集群临时不可用。"
        "技术交流时可结合需求规格说明书与数据库设计说明书中的表结构与 API 列表。",
    )
    add_h(doc, "9.5 实训总结陈述（模板）", 2)
    add_p(
        doc,
        "本小组完成的「新能源充电桩大数据分析项目」实现了课程要求的全部核心指标："
        "MapReduce 七任务超额完成、MySQL charging_bigdata 库含 MR 七表与 ADS 五表、"
        "Python 分析五类图表、机器学习四项预测接口、Vue3+FastAPI 全栈 Web 与 JWT 鉴权，"
        "并在阿里云 Docker 环境 http://115.29.194.137:8080 稳定运行。"
        "项目扩展了智能助手 RAG 与 Datart BI 对接，体现了对企业级大数据平台的理解。",
    )
    add_p(
        doc,
        "通过八周实训，我们从零基础 Hadoop 配置到能独立排查 HDFS→MR→MySQL→API→前端全链路问题，"
        "文档方面自动生成了符合东软规范的宋体 Word 资料。"
        "感谢指导教师在集群网络与 Docker 部署方面的答疑。"
        "【请填写姓名】、【学号】在此郑重声明本报告内容真实，代码与文档均为本组原创完成。",
    )
    add_h(doc, "9.6 致谢", 2)
    add_p(
        doc,
        "感谢东软实训指导教师在项目立项、中期检查与技术评审中的悉心指导；"
        "感谢小组成员在 Hadoop 集群熬夜调试、Docker 部署与前端联调中的互相配合；"
        "感谢开源社区提供的 Hadoop、FastAPI、Vue、ECharts、scikit-learn 等优秀工具，"
        "使我们能在八周内完成从数据到产品的完整闭环。"
        "本报告为实训总结骨架，请各组员填写姓名学号并补充个人心得后提交定稿。",
    )
    add_p(
        doc,
        "项目代码仓库 charging-bigdata 与项目资料提交目录中的 Word 文档由 generate_submission_docs_full.py 统一生成，"
        "确保 SRS、数据库设计、概要设计、部署手册与实训报告内容交叉一致，"
        "均基于 FastAPI、Vue3、MapReduce v1-v7、charging_bigdata MySQL 与 Docker 部署的真实实现编写。",
    )
    add_p(
        doc,
        "演示环境账号 admin@example.com / admin123，公网地址 http://115.29.194.137:8080，"
        "演示前建议提前登录验证图表与预测功能，并准备好 HDFS 与 MR 输出截图作为备用。",
    )
    add_p(doc, "报告完成日期：2026年6月22日。项目版本：CBP V1.3。指导教师审阅签字：__________")

    out = SUBMIT / "05.东软实训综合实训报告/新能源充电桩大数据分析项目-东软实训综合实训报告.docx"
    return save_doc(doc, out)


def build_diagram_guide_docx() -> int:
    """图表绘制规范 Word 版（含 ER 全关系、时序、流程文字说明）。"""
    doc = new_doc()
    _cover_block(doc, "图表绘制规范与关系说明", "CBP-DG-001", "V1.0")

    add_h(doc, "第1章 绘制总则", 1)
    add_p(
        doc,
        "本文档对照东软《新能源充电桩大数据项目》开发手册与项目资料体例规范，"
        "规定功能图、E-R 图、时序图、泳道图、业务流程图及页面效果图的绘制内容与粘贴位置。"
        "项目组使用 draw.io 或 ProcessOn 按本章文字说明作图，导出 PNG 插入各子目录或 Word 占位处。",
    )
    add_bullets(
        doc,
        [
            "架构图、功能图 → 01.需求分析/01.功能图/",
            "业务分析图、泳道图 → 01.需求分析/03、04/",
            "页面效果图 → 01.需求分析/05.页面效果图/",
            "E-R 图 → 02.系统设计/01.数据库设计/02.E-R图/",
            "时序图 → 02.系统设计/02.时序图/",
        ],
    )

    add_h(doc, "第2章 E-R 图绘制（必须画全 17 条关系）", 1)
    add_p(doc, "实体分四类：HDFS 逻辑源（4）、MR 结果表（7）、ADS 表（5）、认证表（4）。视图 3 个。")
    add_table(
        doc,
        ["关系", "起点", "终点", "画法"],
        [
            ["R01~R07", "dsv13r1", "t_voltage_current 等 7 表", "实线箭头，标注 v1~v7"],
            ["R08~R12", "dsv13r2/nvv2t", "ADS 五表", "虚线箭头，标注 ETL"],
            ["R13~R14", "sys_user", "token 表", "实线 1:N 鸦脚"],
            ["R15~R17", "MR 基表", "BI 视图", "虚线 1:1"],
        ],
    )
    add_placeholder_figure(doc, "图2-1 MR与ADS逻辑E-R图", "含全部实体与关系编号")

    add_h(doc, "第3章 时序图绘制", 1)
    add_p(doc, "须绘制至少 4 张 UML 序列图：用户登录、Token 刷新、费用预测、MR 入库。")
    add_bullets(
        doc,
        [
            "登录：用户→LoginView→Nginx→AuthAPI→AuthService→MySQL→返回 JWT；",
            "刷新：Axios 401→/auth/refresh→轮换 refresh_token→重试原请求；",
            "预测：PredictView→POST /predict/fee→PredictService→fee_model.pkl；",
            "入库：load_mr_to_mysql 读 HDFS part-r-00000→循环 UPSERT MySQL。",
        ],
    )
    add_placeholder_figure(doc, "图3-1 用户登录时序图", "02.时序图/用户登录时序图.png")

    add_h(doc, "第4章 业务流程图与泳道图", 1)
    add_p(
        doc,
        "主流程：上传 CSV→MR v1~v7→入库→ADS ETL→训练模型→Docker 部署→用户登录→查看分析预测。"
        "泳道图须含：运营用户、Vue3、Nginx、FastAPI、MySQL 五道。"
    )
    add_placeholder_figure(doc, "图4-1 端到端主业务流程图", "01.业务分析图/")

    add_h(doc, "第5章 页面效果图（对照手册 5.4）", 1)
    add_table(
        doc,
        ["手册节", "路由", "截图文件名"],
        [
            ["5.4.1", "/", "01-系统首页.png"],
            ["5.4.2", "/charging", "03-充电次数分析.png"],
            ["5.4.3", "/soc", "04-SOC折线图.png"],
            ["5.4.5", "/charge-rate", "06-充电速率.png"],
            ["5.4.6", "/performance-report", "07-性能分类报告.png"],
            ["5.4.7~10", "/predict", "08~11 预测各 Tab"],
        ],
    )

    add_h(doc, "第6章 泳道图绘制", 1)
    add_p(doc, "用户访问 Web 系统泳道图须包含五道：运营用户、Vue3 浏览器、Nginx、FastAPI、MySQL。")
    add_table(
        doc,
        ["步骤", "用户", "前端", "Nginx", "API", "DB"],
        [
            ["1", "打开:8080", "加载首页", "静态文件", "-", "-"],
            ["2", "登录", "POST login", "反代", "AuthService", "SELECT user"],
            ["3", "看SOC图", "GET bi/soc-hourly", "反代", "BiService", "SELECT ADS"],
            ["4", "预测费用", "POST predict/fee", "反代", "PredictService", "读pkl"],
        ],
    )

    add_h(doc, "第7章 原型图与页面布局", 1)
    add_p(
        doc,
        "原型图（02.原型图/）可采用低保真线框：首页四卡片、登录双字段、预测四 Tab。"
        "页面效果图须从演示环境 http://115.29.194.137:8080 实际截图，"
        "与手册 5.4.1~5.4.10 页面一一对应，可按手册顺序进行功能说明。",
    )
    add_bullets(
        doc,
        [
            "首页：导航栏 + 新能源充电大数据可视化入口 + BI + 预测 + 登录态；",
            "登录页：ChargingLogin 组件，深色科技风，含演示账号 foot 提示；",
            "分析页：ECharts 全宽图表，支持图表点击放大（ExpandableChartBlock）；",
            "预测页：Element Plus Tab，每 Tab 独立表单与结果卡片；",
            "BI 页：MR 七指标 ECharts 或 Datart iframe 嵌入。",
        ],
    )

    add_h(doc, "第8章 与开发手册章节对照", 1)
    add_table(
        doc,
        ["手册", "图表类型", "提交目录"],
        [
            ["第一章 数据特征", "数据流图", "01.功能图/"],
            ["第二章 HDFS", "存储架构图", "01.功能图/"],
            ["第三章 MR", "批处理流程图", "01.业务分析图/"],
            ["第四章 分析ML", "训练推理流程图", "01.业务分析图/"],
            ["第五章 5.4", "页面效果图", "01.页面效果图/"],
        ],
    )

    add_h(doc, "附录 关系编号完整表", 1)
    add_table(
        doc,
        ["编号", "起点", "终点", "基数"],
        [
            ["R01", "dsv13r1", "t_voltage_current", "1:N"],
            ["R02", "dsv13r1", "t_cell_voltage_range", "1:N"],
            ["R03", "dsv13r1", "t_temperature", "1:N"],
            ["R04", "dsv13r1", "t_energy_capacity", "1:N"],
            ["R05", "dsv13r1", "t_charge_current_stats", "1:N"],
            ["R06", "dsv13r1", "t_voltage_current_relation", "1:N"],
            ["R07", "dsv13r1", "t_soc_temperature", "1:N"],
            ["R08", "dsv13r2", "t_soc_hourly", "1:N"],
            ["R09", "nvv2t", "t_charging_daily", "1:N"],
            ["R10", "nvv2t", "t_charging_monthly", "1:N"],
            ["R11", "dsv13r2", "t_charge_rate_hourly", "1:N"],
            ["R12", "dsv13r2", "t_soc_heatmap", "1:N"],
            ["R13", "sys_user", "sys_refresh_token", "1:N"],
            ["R14", "sys_user", "sys_email_token", "1:N"],
            ["R15", "t_voltage_current", "v_voltage_current", "1:1"],
            ["R16", "t_temperature", "v_temperature", "1:1"],
            ["R17", "t_soc_temperature", "v_soc_temperature", "1:1"],
        ],
    )

    add_h(doc, "附录 B 时序图消息清单", 1)
    add_p(doc, "登录时序须包含消息：submit → POST login → SELECT user → bcrypt verify → INSERT refresh_token → 200 JSON → store localStorage → redirect。")
    add_p(doc, "预测时序须包含：fill form → POST /predict/fee → load pkl → predict → display fee。")
    add_p(doc, "MR 入库时序须包含：open part-r-00000 → parse TSV → UPSERT loop → commit。")

    out = SUBMIT / "00.图表绘制规范/新能源充电桩大数据分析项目-图表绘制规范.docx"
    return save_doc(doc, out)


def _delete_stray_nep_srs():
    stray = SUBMIT / "01.需求分析/06.需求规格说明书/环保公众监督平台-需求规格说明书.docx"
    if stray.exists():
        stray.unlink()
        print(f"已删除遗留文件: {stray}")


def main():
    _delete_stray_nep_srs()

    # 数据字典 xls（公众监督模板格式）
    try:
        from generate_data_dictionary_xls import build as build_xls

        xls_path = build_xls()
        print(f"[OK] 数据字典 xls: {xls_path}")
    except Exception as e:
        print(f"[WARN] 数据字典 xls 生成失败: {e}")

    builders = [
        ("需求规格说明书 (SRS)", "srs", build_srs_docx),
        ("数据库设计说明书", "db", build_db_docx),
        ("数据字典", "data_dict", build_data_dict_docx),
        ("概要设计说明书", "outline", build_outline_docx),
        ("项目部署手册", "deploy", build_deploy_manual_docx),
        ("东软实训综合实训报告", "training", build_training_report_docx),
        ("图表绘制规范", "diagram", build_diagram_guide_docx),
    ]

    print("=" * 60)
    print("新能源充电桩大数据分析项目 — 完整 Word 文档生成")
    print("=" * 60)

    results: list[tuple[str, int, int]] = []
    for label, key, fn in builders:
        n = fn()
        minimum = MIN_CHARS[key]
        results.append((label, n, minimum))
        status = "OK" if n >= minimum else "WARN"
        print(f"[{status}] {label}: {n} 字 (下限 {minimum})")
        if n < minimum:
            print(f"       [WARN] 文档篇幅偏短，请补充技术内容: {label}")

    print("-" * 60)
    total = sum(r[1] for r in results)
    print(f"合计生成 {len(results)} 个文档，总字符数约 {total}")
    print("=" * 60)


if __name__ == "__main__":
    main()
