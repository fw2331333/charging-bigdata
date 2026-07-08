from __future__ import annotations

import json
import logging
from pathlib import Path

from app.core.config import settings
from app.rag.chunk_id import chunk_id, corpus_fingerprint
from app.rag.chunks import KnowledgeChunk
from app.rag.embeddings import TfidfEmbeddingFunction, create_embedding_function

logger = logging.getLogger(__name__)

_COLLECTION = "charging_knowledge"
_MANIFEST = "manifest.json"


class VectorStore:
    """Chroma 持久化向量库 + BGE（优先）/ TF-IDF（回退）。"""

    def __init__(self, chunks: list[KnowledgeChunk]) -> None:
        self.chunks = chunks
        self._chunk_map = {chunk_id(c): c for c in chunks}
        self._dir = Path(settings.RAG_CHROMA_DIR)
        self._dir.mkdir(parents=True, exist_ok=True)
        self._client = None
        self._collection = None
        self._ef = None
        self._embedding_backend = "none"
        self._enabled = settings.RAG_USE_VECTOR
        if self._enabled:
            self._init_collection()

    def _init_collection(self) -> None:
        try:
            import chromadb
        except ImportError as exc:
            logger.warning("Chroma 未安装，向量检索已禁用: %s", exc)
            self._enabled = False
            return

        try:
            self._ef = create_embedding_function(self._dir)
            self._embedding_backend = getattr(self._ef, "backend", "unknown")
        except Exception as exc:
            logger.warning("Embedding 初始化失败，向量检索已禁用: %s", exc)
            self._enabled = False
            return

        self._client = chromadb.PersistentClient(path=str(self._dir))
        self._collection = self._client.get_or_create_collection(
            name=_COLLECTION,
            embedding_function=self._ef,
            metadata={"hnsw:space": "cosine"},
        )
        self._sync_if_needed()

    def _manifest_path(self) -> Path:
        return self._dir / _MANIFEST

    def _read_manifest(self) -> dict | None:
        path = self._manifest_path()
        if not path.exists():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None

    def _write_manifest(self, fingerprint: str) -> None:
        payload = {
            "fingerprint": fingerprint,
            "chunk_count": len(self.chunks),
            "embedding_model": settings.EMBEDDING_MODEL,
            "embedding_backend": self._embedding_backend,
        }
        self._manifest_path().write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _sync_if_needed(self) -> None:
        if not self._collection:
            return
        fp = corpus_fingerprint(self.chunks)
        manifest = self._read_manifest()
        stored_count = self._collection.count()
        if (
            manifest
            and manifest.get("fingerprint") == fp
            and manifest.get("chunk_count") == len(self.chunks)
            and manifest.get("embedding_backend") == self._embedding_backend
            and stored_count == len(self.chunks)
        ):
            return
        self.rebuild()

    def rebuild(self) -> int:
        if not self._enabled or not self._client:
            return 0

        self._ef = create_embedding_function(self._dir)
        self._embedding_backend = getattr(self._ef, "backend", "unknown")

        fp = corpus_fingerprint(self.chunks)
        try:
            self._client.delete_collection(_COLLECTION)
        except Exception:
            pass

        self._collection = self._client.get_or_create_collection(
            name=_COLLECTION,
            embedding_function=self._ef,
            metadata={"hnsw:space": "cosine"},
        )

        ids: list[str] = []
        documents: list[str] = []
        metadatas: list[dict[str, str]] = []
        for chunk in self.chunks:
            cid = chunk_id(chunk)
            ids.append(cid)
            documents.append(f"{chunk.title}\n{chunk.content}")
            metadatas.append({"source": chunk.source, "title": chunk.title})

        if isinstance(self._ef, TfidfEmbeddingFunction):
            self._ef.fit_and_save(documents)

        batch = 32
        for i in range(0, len(ids), batch):
            self._collection.add(
                ids=ids[i : i + batch],
                documents=documents[i : i + batch],
                metadatas=metadatas[i : i + batch],
            )

        self._write_manifest(fp)
        logger.info(
            "RAG 向量索引已重建: %s chunks, backend=%s",
            len(ids),
            self._embedding_backend,
        )
        return len(ids)

    @property
    def enabled(self) -> bool:
        return self._enabled and self._collection is not None

    @property
    def embedding_backend(self) -> str:
        return self._embedding_backend

    def search(self, query: str, top_k: int = 4) -> list[KnowledgeChunk]:
        if not self.enabled or not self._collection:
            return []

        count = self._collection.count()
        if count == 0:
            return []

        try:
            result = self._collection.query(
                query_texts=[query],
                n_results=min(top_k, count),
                include=["metadatas"],
            )
        except Exception as exc:
            logger.warning("向量检索失败，将回退关键词检索: %s", exc)
            return []

        ids = result.get("ids", [[]])[0]
        hits: list[KnowledgeChunk] = []
        for cid in ids:
            chunk = self._chunk_map.get(cid)
            if chunk:
                hits.append(chunk)
        return hits
