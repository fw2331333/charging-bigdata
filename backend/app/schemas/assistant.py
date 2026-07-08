"""智能助手：大模型问答 + BI 数据上下文。"""

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str = Field(..., pattern="^(user|assistant)$")
    content: str = Field(..., min_length=1, max_length=4000)


class AssistantChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    locale: str = Field(default="zh", pattern="^(zh|en)$")
    history: list[ChatMessage] = Field(default_factory=list, max_length=12)


class AssistantChatResponse(BaseModel):
    reply: str
    mode: str = Field(description="llm | rule")
    data_context_included: bool = True
    rag_sources: list[str] = Field(default_factory=list, description="RAG 引用来源")
    rag_mode: str = Field(default="hybrid", description="hybrid | vector | lexical")


class AssistantReindexResponse(BaseModel):
    chunk_count: int
    vector_indexed: int
    embedding_model: str
    embedding_backend: str = Field(description="bge | tfidf | none")
    vector_enabled: bool
