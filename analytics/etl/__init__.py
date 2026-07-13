# -*- coding: utf-8 -*-
"""
离线 ETL 子包：MapReduce 结果 HDFS → MySQL 服务层。

企业级设计原则（与课程「MR 直连 MySQL」对比）：
  - 计算与入库解耦：MR 只写 HDFS，ETL 独立进程负责幂等 upsert
  - 可重跑、可审计：ETL 失败不影响 HDFS 原始结果，便于对账与回补
  - 服务层只读 MySQL：Web API 不依赖 Hadoop 运行时
"""

from analytics.etl.config import PipelineConfig, load_pipeline_config
from analytics.etl.mr_loader import MrToMysqlLoader
from analytics.etl.mr_tasks import MR_ETL_TASKS

__all__ = [
    "MR_ETL_TASKS",
    "MrToMysqlLoader",
    "PipelineConfig",
    "load_pipeline_config",
]
