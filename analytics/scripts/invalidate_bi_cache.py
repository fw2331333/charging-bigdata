"""ETL 完成后通知 FastAPI 清空 BI 查询缓存。"""
from __future__ import annotations

import logging
import os
import urllib.error
import urllib.request

log = logging.getLogger(__name__)


def invalidate_backend_bi_cache(
    backend_url: str | None = None,
    pipeline_secret: str | None = None,
) -> bool:
    base = (backend_url or os.environ.get("BACKEND_URL") or "http://127.0.0.1:8000").rstrip("/")
    secret = pipeline_secret or os.environ.get("PIPELINE_SECRET") or "charging-pipeline-dev"
    url = f"{base}/api/v1/bi/cache/invalidate-pipeline"
    req = urllib.request.Request(
        url,
        method="POST",
        headers={"X-Pipeline-Secret": secret},
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            log.info("BI cache invalidated: %s", body)
            return True
    except urllib.error.URLError as exc:
        log.warning("BI cache invalidate skipped (backend unreachable): %s", exc)
        return False
