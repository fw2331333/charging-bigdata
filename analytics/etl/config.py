# -*- coding: utf-8 -*-
"""流水线环境配置：从 config/pipeline.env 加载，供 ETL / Spark 脚本共用。"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PipelineConfig:
    """离线流水线运行时配置（不含密钥落盘逻辑，由调用方传入 env 文件路径）。"""

    mysql_host: str
    mysql_port: int
    mysql_user: str
    mysql_password: str
    mysql_database: str
    hdfs_output_base: str

    @property
    def mysql_dsn_label(self) -> str:
        return f"{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"


def load_pipeline_env(env_file: Path) -> dict[str, str]:
    """解析 KEY=VALUE 格式 env 文件（自动忽略 # 注释与空行）。"""
    cfg: dict[str, str] = {}
    if not env_file.is_file():
        return cfg
    for raw in env_file.read_text(encoding="utf-8").splitlines():
        line = raw.strip().replace("\r", "")
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        cfg[key.strip()] = value.strip().strip('"').strip("'")
    return cfg


def load_pipeline_config(env_file: Path, hdfs_base_override: str = "") -> PipelineConfig:
    """从 pipeline.env 构建 ETL 所需 MySQL / HDFS 配置。"""
    raw = load_pipeline_env(env_file)
    password = raw.get("MYSQL_PASSWORD", "")
    if not password:
        raise ValueError(f"MySQL 密码为空，请检查 {env_file} 中 MYSQL_PASSWORD")

    return PipelineConfig(
        mysql_host=raw.get("MYSQL_HOST", "10.0.2.2"),
        mysql_port=int(raw.get("MYSQL_PORT", "3306")),
        mysql_user=raw.get("MYSQL_USER", "root"),
        mysql_password=password,
        mysql_database=raw.get("MYSQL_DATABASE", "charging_bigdata"),
        hdfs_output_base=hdfs_base_override or raw.get("HDFS_OUTPUT_BASE", "/Car/output"),
    )
