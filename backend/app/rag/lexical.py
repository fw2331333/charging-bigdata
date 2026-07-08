from __future__ import annotations

import math
import re

from app.rag.chunks import KnowledgeChunk

_TOKEN_RE = re.compile(r"[\u4e00-\u9fff]|[a-zA-Z0-9_]+")


def _tokenize(text: str) -> list[str]:
    return [m.group().lower() for m in _TOKEN_RE.finditer(text or "")]


class LexicalRetriever:
    def __init__(self, chunks: list[KnowledgeChunk]) -> None:
        self.chunks = chunks
        self._df: dict[str, int] = {}
        for chunk in chunks:
            for token in set(_tokenize(chunk.title + " " + chunk.content)):
                self._df[token] = self._df.get(token, 0) + 1
        self._n = max(len(chunks), 1)

    def search(self, query: str, top_k: int = 4) -> list[KnowledgeChunk]:
        q_tokens = _tokenize(query)
        if not q_tokens:
            return []

        scored: list[tuple[float, int]] = []
        for idx, chunk in enumerate(self.chunks):
            corpus = _tokenize(chunk.title + " " + chunk.content)
            token_set = set(corpus)
            score = 0.0
            for token in q_tokens:
                if token in token_set:
                    idf = math.log((self._n + 1) / (self._df.get(token, 0) + 1)) + 1.0
                    score += idf
                if token in chunk.title.lower():
                    score += 1.5
            if score > 0:
                scored.append((score, idx))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [self.chunks[i] for _, i in scored[:top_k]]
