from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class KnowledgeChunk:
    source: str
    title: str
    content: str

    @property
    def citation(self) -> str:
        return f"{self.source} · {self.title}"

    def as_context_block(self) -> str:
        return f"[{self.citation}]\n{self.content.strip()}"
