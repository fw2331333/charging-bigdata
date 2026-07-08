from __future__ import annotations

from dataclasses import dataclass

from app.core.config import settings
from app.rag.chunk_id import chunk_id
from app.rag.chunks import KnowledgeChunk
from app.rag.indexer import load_knowledge_chunks
from app.rag.lexical import LexicalRetriever
from app.rag.vector_store import VectorStore

_RRF_K = 60


@dataclass(frozen=True)
class SearchResult:
    chunks: list[KnowledgeChunk]
    mode: str  # hybrid | vector | lexical


class HybridRetriever:
    """BGE 向量检索 + 关键词检索，RRF 融合排序。"""

    def __init__(self, chunks: list[KnowledgeChunk]) -> None:
        self.chunks = chunks
        self._lexical = LexicalRetriever(chunks)
        self._vector = VectorStore(chunks)

    @property
    def vector_enabled(self) -> bool:
        return self._vector.enabled

    @property
    def embedding_backend(self) -> str:
        return self._vector.embedding_backend

    def rebuild_index(self) -> int:
        return self._vector.rebuild()

    def search(self, query: str, top_k: int | None = None) -> list[KnowledgeChunk]:
        return self.search_with_meta(query, top_k).chunks

    def search_with_meta(self, query: str, top_k: int | None = None) -> SearchResult:
        k = top_k or settings.RAG_TOP_K
        pool = max(k * 3, 8)

        vector_hits = self._vector.search(query, top_k=pool) if self._vector.enabled else []
        lexical_hits = self._lexical.search(query, top_k=pool)

        if vector_hits and lexical_hits:
            return SearchResult(self._rrf_merge(vector_hits, lexical_hits, k), "hybrid")
        if vector_hits:
            return SearchResult(vector_hits[:k], "vector")
        return SearchResult(lexical_hits[:k], "lexical")

    def _rrf_merge(
        self,
        vector_hits: list[KnowledgeChunk],
        lexical_hits: list[KnowledgeChunk],
        top_k: int,
    ) -> list[KnowledgeChunk]:
        scores: dict[str, float] = {}
        chunk_by_id: dict[str, KnowledgeChunk] = {}

        for rank, chunk in enumerate(vector_hits):
            cid = chunk_id(chunk)
            chunk_by_id[cid] = chunk
            scores[cid] = scores.get(cid, 0.0) + 1.0 / (_RRF_K + rank + 1)

        for rank, chunk in enumerate(lexical_hits):
            cid = chunk_id(chunk)
            chunk_by_id[cid] = chunk
            scores[cid] = scores.get(cid, 0.0) + 1.0 / (_RRF_K + rank + 1)

        ordered = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [chunk_by_id[cid] for cid, _ in ordered[:top_k]]


_retriever: HybridRetriever | None = None


def get_retriever() -> HybridRetriever:
    global _retriever
    if _retriever is None:
        _retriever = HybridRetriever(load_knowledge_chunks())
    return _retriever


def reset_retriever() -> HybridRetriever:
    global _retriever
    _retriever = HybridRetriever(load_knowledge_chunks())
    return _retriever
