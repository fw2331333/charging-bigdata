"""智能助手 API。"""

import json
from collections.abc import AsyncIterator

import pymysql
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.api.deps import get_current_user, get_db, require_admin
from app.core.config import settings
from app.rag.retriever import reset_retriever
from app.schemas.assistant import (
    AssistantChatRequest,
    AssistantChatResponse,
    AssistantReindexResponse,
)
from app.schemas.auth import UserInfo
from app.services.assistant_service import AssistantService

router = APIRouter(prefix="/assistant", tags=["智能助手"])
service = AssistantService()


def _format_sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


async def _stream_events(
    req: AssistantChatRequest,
    db: pymysql.connections.Connection,
) -> AsyncIterator[str]:
    try:
        yield _format_sse("status", {"phase": "preparing"})
        data_ctx = service.build_data_context(db)
        rag_chunks, rag_mode = service.retrieve_context(req.message)
        rag_sources = [c.citation for c in rag_chunks]
        yield _format_sse("status", {"phase": "generating"})
        async for event, payload in service.stream_chat_prepared(
            req, data_ctx, rag_chunks, rag_mode, rag_sources
        ):
            yield _format_sse(event, payload)
    except Exception as exc:
        yield _format_sse("error", {"message": str(exc)})


@router.post("/chat/stream", summary="数据智能问答（SSE 流式）")
async def chat_stream(
    req: AssistantChatRequest,
    _: UserInfo = Depends(get_current_user),
    db: pymysql.connections.Connection = Depends(get_db),
) -> StreamingResponse:
    return StreamingResponse(
        _stream_events(req, db),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/chat", response_model=AssistantChatResponse, summary="数据智能问答")
async def chat(
    req: AssistantChatRequest,
    _: UserInfo = Depends(get_current_user),
    db: pymysql.connections.Connection = Depends(get_db),
) -> AssistantChatResponse:
    reply, mode, rag_sources, rag_mode = await service.chat(db, req)
    return AssistantChatResponse(
        reply=reply,
        mode=mode,
        rag_sources=rag_sources,
        rag_mode=rag_mode,
    )


@router.post("/reindex", response_model=AssistantReindexResponse, summary="重建 RAG 向量索引（管理员）")
async def reindex(_: UserInfo = Depends(require_admin)) -> AssistantReindexResponse:
    retriever = reset_retriever()
    vector_indexed = retriever.rebuild_index()
    return AssistantReindexResponse(
        chunk_count=len(retriever.chunks),
        vector_indexed=vector_indexed,
        embedding_model=settings.EMBEDDING_MODEL,
        embedding_backend=getattr(retriever, "embedding_backend", "none"),
        vector_enabled=retriever.vector_enabled,
    )
