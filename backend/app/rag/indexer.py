from __future__ import annotations

import re
from pathlib import Path

from app.rag.chunks import KnowledgeChunk

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
_DOC_GLOBS = ("docs/*.md", "README.md", "sql/seed/README.md")


def _builtin_chunks() -> list[KnowledgeChunk]:
    return [
        KnowledgeChunk(
            source="系统功能",
            title="数据分析模块",
            content=(
                "bda1 充电时间与次数频率：/bda1；"
                "bda2 每小时平均 SOC：/bda2；"
                "bda3 充电时间分布（时/日/月）：/bda3；"
                "bda4 平均充电速率：/bda4；"
                "bda5 性能指标分类报告：/bda5。"
            ),
        ),
        KnowledgeChunk(
            source="系统功能",
            title="机器学习预测",
            content=(
                "预测剩余电量 SOC：/predict/soc；"
                "预测充电时间：/predict/duration；"
                "预测充电费用：/predict/fee；"
                "预测充电平台：/predict/platform。"
                "模型由 analytics 训练脚本产出，指标可在 bda5 查看。"
            ),
        ),
        KnowledgeChunk(
            source="系统功能",
            title="BI 可视化大屏",
            content=(
                "七图 BI 大屏路径 /mr-bi，对应手册 v1–v7 图表，"
                "可从首页按钮进入；支持点击下钻到各分析页。"
                "可选 Datart 外链大屏见部署手册。"
            ),
        ),
        KnowledgeChunk(
            source="数据表 ADS",
            title="充电次数汇总",
            content=(
                "t_charging_daily：record_date, charge_count 每日充电次数；"
                "t_charging_monthly：record_month, charge_count 每月充电次数。"
                "用于 bda1/bda3 图表与助手数据摘要。"
            ),
        ),
        KnowledgeChunk(
            source="数据表 ADS",
            title="SOC 与充电速率",
            content=(
                "t_soc_hourly：hour_key, avg_soc 每小时平均 SOC；"
                "t_charge_rate_hourly：hour_key, avg_rate 每小时平均充电速率。"
                "用于 bda2、bda4 及 SOC 相关问答。"
            ),
        ),
        KnowledgeChunk(
            source="数据流水线",
            title="HDFS 与 MapReduce",
            content=(
                "原始 CSV 上传 HDFS /Car/（dsv13r1、dsv13r2、nvv2t、nvv2t_md）；"
                "MapReduce 七任务产出写入 MySQL；"
                "Python/Spark 分析经 ETL 进入 ADS 表供 FastAPI BI 接口查询。"
            ),
        ),
        KnowledgeChunk(
            source="认证",
            title="登录与演示账号",
            content=(
                "邮箱登录 POST /api/v1/auth/login；"
                "演示账号 admin@example.com / admin123（管理员）、"
                "user@example.com / user123。"
                "双 Token：Access 约 30 分钟，Refresh 约 7 天。"
            ),
        ),
    ]


def _split_markdown(text: str, source: str) -> list[KnowledgeChunk]:
    parts = re.split(r"(?=^#{1,3}\s+)", text, flags=re.MULTILINE)
    chunks: list[KnowledgeChunk] = []
    for part in parts:
        block = part.strip()
        if not block:
            continue
        lines = block.splitlines()
        title = lines[0].lstrip("#").strip() if lines else source
        body = "\n".join(lines[1:]).strip() if len(lines) > 1 else block
        if len(body) < 40 and title == source:
            body = block
        for sub in _window_text(body, 900, 120):
            chunks.append(KnowledgeChunk(source=source, title=title, content=sub))
    return chunks


def _window_text(text: str, size: int, overlap: int) -> list[str]:
    text = text.strip()
    if len(text) <= size:
        return [text] if text else []
    windows: list[str] = []
    start = 0
    while start < len(text):
        windows.append(text[start : start + size])
        if start + size >= len(text):
            break
        start += max(size - overlap, 1)
    return windows


def load_knowledge_chunks() -> list[KnowledgeChunk]:
    chunks = _builtin_chunks()
    for pattern in _DOC_GLOBS:
        for path in sorted(_PROJECT_ROOT.glob(pattern)):
            try:
                text = path.read_text(encoding="utf-8")
            except OSError:
                continue
            rel = path.relative_to(_PROJECT_ROOT).as_posix()
            chunks.extend(_split_markdown(text, rel))
    return chunks
