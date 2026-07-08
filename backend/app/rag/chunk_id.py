from __future__ import annotations

import hashlib

from app.rag.chunks import KnowledgeChunk


def chunk_id(chunk: KnowledgeChunk) -> str:
    raw = f"{chunk.source}\0{chunk.title}\0{chunk.content}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:32]


def corpus_fingerprint(chunks: list[KnowledgeChunk]) -> str:
    ids = sorted(chunk_id(c) for c in chunks)
    return hashlib.sha256("\n".join(ids).encode("utf-8")).hexdigest()
