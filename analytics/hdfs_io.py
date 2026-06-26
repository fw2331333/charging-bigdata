# -*- coding: utf-8 -*-
"""HDFS 读写工具：通过 WebHDFS 读取用户上传至 /Car/ 的 CSV，不在本地仓库存放数据集。"""

from __future__ import annotations

import os
from typing import Iterator
from urllib.parse import quote

import requests

# 默认 NameNode WebHDFS 地址，可通过环境变量覆盖
DEFAULT_NN = os.getenv("HDFS_NN_HOST", "http://hadoop-master:9870")
DEFAULT_USER = os.getenv("HDFS_USER", "hadoop")
HDFS_BASE = "/Car"


def _webhdfs_url(path: str, op: str, user: str | None = None) -> str:
  """构造 WebHDFS 请求 URL。"""
  user = user or DEFAULT_USER
  normalized = path if path.startswith("/") else f"{HDFS_BASE}/{path}"
  return f"{DEFAULT_NN}/webhdfs/v1{quote(normalized)}?op={op}&user.name={quote(user)}"


def read_lines(hdfs_path: str, user: str | None = None, chunk_size: int = 65536) -> Iterator[str]:
  """
  流式读取 HDFS 文本文件行（适合大 CSV）。
  示例：read_lines("/Car/dsv13r2.csv")
  """
  url = _webhdfs_url(hdfs_path, "OPEN", user)
  with requests.get(url, stream=True, timeout=120) as resp:
    resp.raise_for_status()
    buffer = ""
    for chunk in resp.iter_content(chunk_size=chunk_size, decode_unicode=True):
      if not chunk:
        continue
      buffer += chunk
      while "\n" in buffer:
        line, buffer = buffer.split("\n", 1)
        yield line.rstrip("\r")
    if buffer:
      yield buffer.rstrip("\r")


def exists(hdfs_path: str, user: str | None = None) -> bool:
  """检查 HDFS 路径是否存在。"""
  url = _webhdfs_url(hdfs_path, "GETFILESTATUS", user)
  resp = requests.get(url, timeout=30)
  return resp.status_code == 200
