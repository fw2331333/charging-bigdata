from __future__ import annotations

import logging
import os
import ssl
from pathlib import Path
from typing import TYPE_CHECKING

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer

from app.core.config import settings

if TYPE_CHECKING:
    from chromadb.api.types import Documents, Embeddings

logger = logging.getLogger(__name__)

_VECTORIZER_FILE = "tfidf_vectorizer.joblib"


def _apply_ssl_policy() -> None:
    if not settings.RAG_INSECURE_SSL:
        try:
            import certifi

            ca = certifi.where()
            os.environ.setdefault("SSL_CERT_FILE", ca)
            os.environ.setdefault("REQUESTS_CA_BUNDLE", ca)
        except ImportError:
            pass
        return

    logger.warning("RAG_INSECURE_SSL=true：尝试跳过 SSL 校验下载 BGE（仅开发环境）")
    ssl._create_default_https_context = ssl._create_unverified_context  # noqa: SLF001
    os.environ["HF_HUB_DISABLE_SSL_VERIFICATION"] = "1"


def _try_bge_embedding(model_name: str):
    _apply_ssl_policy()
    from fastembed import TextEmbedding

    return TextEmbedding(model_name=model_name)


class BgeEmbeddingFunction:
    """BGE 中文向量（fastembed ONNX + BAAI/bge-small-zh-v1.5）。"""

    backend = "bge"

    def __init__(self, model_name: str) -> None:
        logger.info("加载 BGE Embedding: %s", model_name)
        self._model = _try_bge_embedding(model_name)

    def __call__(self, input: Documents) -> Embeddings:
        return [vec.tolist() for vec in self._model.embed(input)]

    def embed_query(self, input: str | list[str]) -> Embeddings:
        texts = [input] if isinstance(input, str) else input
        return self.__call__(texts)

    def name(self) -> str:
        return "bge-fastembed"


class TfidfEmbeddingFunction:
    """离线 TF-IDF 向量（BGE 不可用时回退，仍可走 Chroma 语义近邻）。"""

    backend = "tfidf"

    def __init__(self, store_dir: Path) -> None:
        self._path = store_dir / _VECTORIZER_FILE
        self._vectorizer: TfidfVectorizer | None = None
        if self._path.exists():
            self._vectorizer = joblib.load(self._path)

    def fit_and_save(self, documents: list[str]) -> None:
        self._vectorizer = TfidfVectorizer(
            analyzer="char",
            ngram_range=(1, 2),
            max_features=2048,
        )
        self._vectorizer.fit(documents)
        joblib.dump(self._vectorizer, self._path)
        logger.info("TF-IDF 向量器已训练并保存: %s 文档", len(documents))

    def __call__(self, input: Documents) -> Embeddings:
        if self._vectorizer is None:
            raise RuntimeError("TF-IDF 向量器未就绪，请先重建索引")
        matrix = self._vectorizer.transform(input).toarray()
        return [row.tolist() for row in matrix]

    def embed_query(self, input: str | list[str]) -> Embeddings:
        texts = [input] if isinstance(input, str) else input
        return self.__call__(texts)

    def name(self) -> str:
        return "tfidf-fallback"


def create_embedding_function(store_dir: Path):
    """优先 BGE；失败则使用本地 TF-IDF。"""
    if settings.RAG_USE_VECTOR:
        try:
            return BgeEmbeddingFunction(settings.EMBEDDING_MODEL)
        except Exception as exc:
            logger.warning("BGE 加载失败，回退 TF-IDF 向量: %s", exc)

    logger.info("使用 TF-IDF 向量检索（离线模式）")
    return TfidfEmbeddingFunction(store_dir)
