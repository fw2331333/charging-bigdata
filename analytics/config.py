# -*- coding: utf-8 -*-
"""分析模块配置。"""

import os
from pathlib import Path

# 模型输出目录（运行时生成，不提交数据集）
OUTPUT_DIR = Path(__file__).resolve().parent / "output"
MODELS_DIR = OUTPUT_DIR / "models"

HDFS_NN_HOST = os.getenv("HDFS_NN_HOST", "http://hadoop-master:9870")
HDFS_USER = os.getenv("HDFS_USER", "hadoop")

MODELS_DIR.mkdir(parents=True, exist_ok=True)
