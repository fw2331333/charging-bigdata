# -*- coding: utf-8 -*-
"""
MapReduce 结果装载器：HDFS part-r-00000 → MySQL（幂等 UPSERT）。

设计说明：
  - 使用 mysql CLI + 临时 SQL 文件批量写入，避免在 Reducer 内持有 JDBC 连接
  - ON DUPLICATE KEY UPDATE 保证流水线可重复执行（企业批处理常见 idempotent 模式）
"""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import List, Optional, Tuple

from analytics.etl.config import PipelineConfig
from analytics.etl.mr_tasks import MR_ETL_TASKS, MrEtlTask

log = logging.getLogger("etl.mr_loader")


class MrToMysqlLoader:
    """将 MR 输出目录批量导入 MySQL 服务层。"""

    def __init__(self, cfg: PipelineConfig) -> None:
        self.cfg = cfg

    # ------------------------------------------------------------------ HDFS I/O
    def _hdfs_get(self, hdfs_path: str, local_file: Path) -> None:
        local_file.parent.mkdir(parents=True, exist_ok=True)
        subprocess.check_call(["hdfs", "dfs", "-get", "-f", hdfs_path, str(local_file)])

    # ------------------------------------------------------------------ 解析 MR 行
    @staticmethod
    def _parse_line(line: str) -> Optional[Tuple[str, List[float]]]:
        line = line.strip()
        if not line:
            return None
        parts = line.split("\t")
        if len(parts) < 3:
            return None
        key = parts[0]
        try:
            metrics = [float(x) for x in parts[1:]]
        except ValueError:
            return None
        return key, metrics

    @staticmethod
    def _sql_quote(value: str) -> str:
        return "'" + value.replace("\\", "\\\\").replace("'", "''") + "'"

    # ------------------------------------------------------------------ MySQL CLI
    def _mysql_cmd(self) -> List[str]:
        c = self.cfg
        return [
            "mysql",
            "-h", c.mysql_host,
            "-P", str(c.mysql_port),
            "-u", c.mysql_user,
            f"-p{c.mysql_password}",
            c.mysql_database,
        ]

    def test_connection(self) -> None:
        subprocess.check_call(
            self._mysql_cmd() + ["-e", "SELECT 1;"],
            stdout=subprocess.DEVNULL,
        )

    def _load_part_file(self, task: MrEtlTask, file_path: Path) -> int:
        columns = task.columns
        table = task.table
        updates = ", ".join(f"{col}=VALUES({col})" for col in columns[1:])
        col_list = ", ".join(columns)
        rows = 0
        fd, sql_path = tempfile.mkstemp(prefix="cbp_etl_", suffix=".sql")
        os.close(fd)

        try:
            with open(sql_path, "w", encoding="utf-8") as out, file_path.open("r", encoding="utf-8") as handle:
                for line in handle:
                    parsed = self._parse_line(line)
                    if parsed is None:
                        continue
                    key, metrics = parsed
                    if len(metrics) < len(columns) - 1:
                        continue
                    vals = [self._sql_quote(key)]
                    vals.extend(str(m) for m in metrics[: len(columns) - 1])
                    out.write(
                        f"INSERT INTO {table} ({col_list}) VALUES ({', '.join(vals)}) "
                        f"ON DUPLICATE KEY UPDATE {updates};\n"
                    )
                    rows += 1

            if rows == 0:
                return 0

            with open(sql_path, "r", encoding="utf-8") as sql_in:
                subprocess.check_call(self._mysql_cmd(), stdin=sql_in)
            return rows
        finally:
            try:
                os.unlink(sql_path)
            except OSError:
                pass

    # ------------------------------------------------------------------ 批量入口
    def run(self, local_dir: Optional[Path] = None) -> int:
        """
        执行全部 v1~v7 装载。

        :param local_dir: 若指定则直接读本地 v1..v7 目录；否则从 HDFS 拉取到临时目录
        :return: 写入/更新总行数
        """
        tmp_dir: Optional[str] = None
        hdfs_base = self.cfg.hdfs_output_base.rstrip("/")
        total = 0

        try:
            if local_dir is not None:
                base = local_dir
            else:
                tmp_dir = tempfile.mkdtemp(prefix="cbp_mr_")
                base = Path(tmp_dir)

            for task in MR_ETL_TASKS:
                part = base / task.code / "part-r-00000"
                if not part.exists():
                    if local_dir is not None:
                        log.warning("[SKIP] %s: missing %s", task.code, part)
                        continue
                    hdfs_path = f"{hdfs_base}/{task.code}/part-r-00000"
                    log.info("hdfs get %s", hdfs_path)
                    self._hdfs_get(hdfs_path, part)

                count = self._load_part_file(task, part)
                log.info("[OK] %s -> %s: %d rows", task.code, task.table, count)
                total += count

            log.info("ETL done. Total rows loaded/updated: %d", total)
            return total
        finally:
            if tmp_dir:
                shutil.rmtree(tmp_dir, ignore_errors=True)
