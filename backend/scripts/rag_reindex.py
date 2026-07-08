#!/usr/bin/env python3
"""离线重建 RAG 向量索引（Chroma + BGE）。"""

from app.core.config import settings
from app.rag.retriever import reset_retriever


def main() -> None:
    retriever = reset_retriever()
    count = retriever.rebuild_index()
    print(f"chunks={len(retriever.chunks)} indexed={count} model={settings.EMBEDDING_MODEL}")


if __name__ == "__main__":
    main()
