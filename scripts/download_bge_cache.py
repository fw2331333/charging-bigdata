#!/usr/bin/env python3
"""
下载 fastembed 使用的 BGE 中文向量模型到本地缓存。

fastembed 对 BAAI/bge-small-zh-v1.5 的下载顺序：
  1) HuggingFace: Qdrant/bge-small-zh-v1.5
  2) 回退 Google: fast-bge-small-zh-v1.5.tar.gz（国内 ECS 常不可达）

用法（项目根目录）：
  python scripts/download_bge_cache.py
  python scripts/download_bge_cache.py --cache-dir ./fastembed_cache
  python scripts/download_bge_cache.py --tar /path/to/fast-bge-small-zh-v1.5.tar.gz

Docker 部署：下载完成后将 fastembed_cache 目录留在服务器，compose 已挂载到 /app/fastembed_cache。
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CACHE = ROOT / "fastembed_cache"
MODEL_NAME = "BAAI/bge-small-zh-v1.5"
HF_REPO = "Qdrant/bge-small-zh-v1.5"
GCS_TAR_URL = "https://storage.googleapis.com/qdrant-fastembed/fast-bge-small-zh-v1.5.tar.gz"
TAR_DIR_NAME = "fast-bge-small-zh-v1.5"


def _apply_hf_mirror() -> None:
    os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")
    # 镜像站 + Xet 存储常 401，强制走传统 LFS 下载
    os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
    os.environ.setdefault("HF_HUB_ENABLE_HF_TRANSFER", "0")


def _has_bge_files(cache_dir: Path) -> bool:
    tar_layout = cache_dir / TAR_DIR_NAME / "model_optimized.onnx"
    if tar_layout.exists():
        return True
    for path in cache_dir.rglob("model_optimized.onnx"):
        if "bge-small-zh" in str(path).lower():
            return True
    return False


def download_from_hf_mirror(cache_dir: Path) -> Path | None:
    _apply_hf_mirror()
    try:
        from huggingface_hub import snapshot_download
    except ImportError:
        print("[skip] 未安装 huggingface_hub，请 pip install huggingface_hub")
        return None

    print(f"[1/3] 从 HF 镜像下载 {HF_REPO} → {cache_dir}")
    try:
        path = snapshot_download(
            repo_id=HF_REPO,
            cache_dir=str(cache_dir),
            allow_patterns=[
                "*.onnx",
                "*.json",
                "*.txt",
                "tokenizer*",
                "special_tokens_map.json",
            ],
        )
        print(f"      HF 镜像完成: {path}")
        return Path(path)
    except Exception as exc:
        print(f"      HF 镜像失败: {exc}")
        return None


def download_from_gcs_tar(cache_dir: Path, tar_path: Path | None = None) -> Path | None:
    cache_dir.mkdir(parents=True, exist_ok=True)
    target_dir = cache_dir / TAR_DIR_NAME
    if target_dir.exists() and (target_dir / "model_optimized.onnx").exists():
        print(f"[2/3] 已存在 {target_dir}，跳过 tar 解压")
        return target_dir

    tar_file = tar_path or (cache_dir / f"{TAR_DIR_NAME}.tar.gz")
    if tar_path is None:
        print(f"[2/3] 从 Google 下载 tar（国内可能失败）: {GCS_TAR_URL}")
        try:
            import httpx

            with httpx.stream("GET", GCS_TAR_URL, timeout=120.0, follow_redirects=True) as res:
                res.raise_for_status()
                with tar_file.open("wb") as f:
                    for chunk in res.iter_bytes():
                        f.write(chunk)
            print(f"      已保存 {tar_file}")
        except Exception as exc:
            print(f"      Google tar 下载失败: {exc}")
            print("      请在本机浏览器下载后 scp 到服务器，再执行：")
            print(f"        python scripts/download_bge_cache.py --tar {TAR_DIR_NAME}.tar.gz")
            print(f"      下载地址: {GCS_TAR_URL}")
            print(f"      或镜像站搜索: {HF_REPO}")
            return None
    elif not tar_file.is_file():
        print(f"      找不到 tar 文件: {tar_file}")
        return None
    else:
        print(f"[2/3] 使用本地 tar: {tar_file}")

    tmp_dir = cache_dir / "tmp"
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)
    tmp_dir.mkdir(parents=True, exist_ok=True)

    print(f"      解压到 {tmp_dir}")
    with tarfile.open(tar_file, "r:gz") as tar:
        tar.extractall(path=tmp_dir)

    extracted = tmp_dir / TAR_DIR_NAME
    if not extracted.exists():
        # 有些包解压后只有一层子目录
        children = [p for p in tmp_dir.iterdir() if p.is_dir()]
        if len(children) == 1:
            extracted = children[0]

    if not (extracted / "model_optimized.onnx").exists():
        print(f"      解压后未找到 model_optimized.onnx: {extracted}")
        return None

    if target_dir.exists():
        shutil.rmtree(target_dir)
    extracted.rename(target_dir)
    shutil.rmtree(tmp_dir, ignore_errors=True)
    if tar_path is None and tar_file.exists():
        tar_file.unlink(missing_ok=True)

    print(f"      tar 解压完成: {target_dir}")
    return target_dir


def verify_fastembed(cache_dir: Path) -> None:
    print("[3/3] 验证 fastembed 加载（local_files_only=True）")
    _apply_hf_mirror()
    os.environ["HF_HUB_OFFLINE"] = "1"

    from fastembed import TextEmbedding

    model = TextEmbedding(
        model_name=MODEL_NAME,
        cache_dir=str(cache_dir),
        local_files_only=True,
    )
    vec = next(model.embed(["充电大数据测试"]))
    print(f"      OK — 向量维度 {len(vec)}，缓存目录: {cache_dir.resolve()}")


def main() -> int:
    parser = argparse.ArgumentParser(description="下载 BGE fastembed 缓存")
    parser.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE)
    parser.add_argument("--tar", type=Path, default=None, help="已下载的 fast-bge-small-zh-v1.5.tar.gz")
    parser.add_argument("--skip-verify", action="store_true")
    args = parser.parse_args()

    cache_dir = args.cache_dir.resolve()
    cache_dir.mkdir(parents=True, exist_ok=True)

    if _has_bge_files(cache_dir):
        print(f"检测到已有 BGE 缓存: {cache_dir}")
    else:
        download_from_hf_mirror(cache_dir)
        if not _has_bge_files(cache_dir):
            download_from_gcs_tar(cache_dir, args.tar)

    if not _has_bge_files(cache_dir):
        print("\n失败：未找到 model_optimized.onnx。请用 --tar 指定本机下载的 tar 包后重试。")
        return 1

    if not args.skip_verify:
        try:
            verify_fastembed(cache_dir)
        except Exception as exc:
            print(f"\n验证失败: {exc}")
            return 1

    print("\n完成。Docker 部署请确保 compose 挂载 fastembed_cache 并设置 RAG_USE_VECTOR=true。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
