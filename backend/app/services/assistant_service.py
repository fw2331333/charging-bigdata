"""智能助手：RAG + BI 摘要 + DeepSeek 大模型。"""

from __future__ import annotations

import asyncio
import json
import re
import time
from collections.abc import AsyncIterator

import httpx
import pymysql

from app.core.config import settings
from app.rag.chunks import KnowledgeChunk
from app.rag.retriever import get_retriever
from app.schemas.assistant import AssistantChatRequest
from app.services.bi_service import BiService
_NAV_ZH = {
    "/": "首页",
    "/bda1": "充电时间与次数频率分析",
    "/bda2": "每时电池平均SOC",
    "/bda3": "充电时间分布图分析",
    "/bda4": "平均充电速率图分析",
    "/bda5": "性能指标分类分析报告",
    "/mr-bi": "新能源充电大数据可视化（七图大屏）",
    "/predict/soc": "预测剩余电量",
    "/predict/duration": "预测充电时间",
    "/predict/fee": "预测充电费用",
    "/predict/platform": "预测充电平台",
}

_NAV_EN = {
    "/": "Home",
    "/bda1": "Charging time & frequency",
    "/bda2": "Hourly average SOC",
    "/bda3": "Charging time distribution",
    "/bda4": "Average charging rate",
    "/bda5": "Performance classification report",
    "/mr-bi": "EV charging visualization (7 charts)",
    "/predict/soc": "Predict remaining SOC",
    "/predict/duration": "Predict charging duration",
    "/predict/fee": "Predict charging fee",
    "/predict/platform": "Predict charging platform",
}


class AssistantService:
    def __init__(self) -> None:
        self.bi = BiService()

    @property
    def retriever(self):
        return get_retriever()

    def build_data_context(self, conn: pymysql.connections.Connection) -> str:
        lines: list[str] = []
        try:
            daily = self.bi.list_charging_daily(conn, 14)
            if daily:
                latest = daily[-1]
                lines.append(
                    f"最近一日({latest.record_date})充电次数: {latest.charge_count}; "
                    f"近14日合计: {sum(r.charge_count for r in daily)}"
                )
            monthly = self.bi.list_charging_monthly(conn, 6)
            if monthly:
                lines.append(
                    "近月充电次数: "
                    + ", ".join(f"{m.record_month}={m.charge_count}" for m in monthly[-6:])
                )
            hourly_soc = self.bi.list_soc_hourly(conn, 24)
            if hourly_soc:
                avg_soc = sum(r.avg_soc for r in hourly_soc) / len(hourly_soc)
                lines.append(f"近24小时平均SOC约 {avg_soc:.1f}%")
            rate = self.bi.list_charge_rate_hourly(conn, 24)
            if rate:
                avg_rate = sum(abs(r.avg_rate) for r in rate) / len(rate)
                lines.append(f"近24小时平均充电速率指标约 {avg_rate:.4f}")
        except Exception as exc:
            lines.append(f"(BI 摘要获取部分失败: {exc})")
        return "\n".join(lines) if lines else "暂无 BI 汇总数据（请确认 MySQL 已导入演示数据）"

    def retrieve_context(self, query: str, top_k: int | None = None) -> tuple[list[KnowledgeChunk], str]:
        k = top_k or settings.RAG_TOP_K
        result = self.retriever.search_with_meta(query, top_k=k)
        return result.chunks, result.mode

    def reindex(self) -> tuple[int, int, bool]:
        retriever = self.retriever
        count = retriever.rebuild_index()
        return len(retriever.chunks), count, retriever.vector_enabled

    def _nav_text(self, locale: str) -> str:
        nav = _NAV_EN if locale == "en" else _NAV_ZH
        return "\n".join(f"- {path}: {label}" for path, label in nav.items())

    def _system_prompt(
        self,
        locale: str,
        data_ctx: str,
        rag_chunks: list[KnowledgeChunk],
    ) -> str:
        rag_block = "\n\n---\n\n".join(c.as_context_block() for c in rag_chunks)
        if locale == "en":
            return (
                "You are the EV charging big-data assistant (Neusoft demo). "
                "Answer using ONLY the retrieved knowledge, BI summary, and navigation. "
                "Cite doc titles when helpful. Suggest routes like /bda3. "
                "If context is insufficient, say so.\n\n"
                f"Retrieved knowledge:\n{rag_block or '(none)'}\n\n"
                f"BI summary:\n{data_ctx}\n\nNavigation:\n{self._nav_text(locale)}"
            )
        return (
            "你是东软新能源充电桩大数据分析系统的智能助手。"
            "请优先依据下方「检索到的项目知识」与 BI 数据摘要作答，可引用文档标题；"
            "引导用户前往对应路径（如 /bda4）。知识不足时请如实说明。\n\n"
            f"检索到的项目知识：\n{rag_block or '（无）'}\n\n"
            f"BI 数据摘要：\n{data_ctx}\n\n功能导航：\n{self._nav_text(locale)}"
        )

    def _build_messages(
        self,
        req: AssistantChatRequest,
        data_ctx: str,
        rag_chunks: list[KnowledgeChunk],
    ) -> list[dict[str, str]]:
        messages: list[dict[str, str]] = [
            {"role": "system", "content": self._system_prompt(req.locale, data_ctx, rag_chunks)},
        ]
        for h in req.history[-8:]:
            messages.append({"role": h.role, "content": h.content})
        messages.append({"role": "user", "content": req.message})
        return messages

    def _llm_url(self) -> str:
        base = settings.LLM_BASE_URL.rstrip("/")
        if not base.endswith("/v1"):
            base = f"{base}/v1"
        return f"{base}/chat/completions"

    def _llm_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {settings.LLM_API_KEY}",
            "Content-Type": "application/json",
        }

    async def chat(
        self,
        conn: pymysql.connections.Connection,
        req: AssistantChatRequest,
    ) -> tuple[str, str, list[str], str]:
        data_ctx = self.build_data_context(conn)
        rag_chunks, rag_mode = self.retrieve_context(req.message)
        rag_sources = [c.citation for c in rag_chunks]

        if settings.LLM_API_KEY and settings.LLM_BASE_URL:
            try:
                reply = await self._llm_chat(req, data_ctx, rag_chunks)
                return reply, "llm", rag_sources, rag_mode
            except Exception:
                pass

        return self._rule_reply(req, data_ctx, rag_chunks), "rule", rag_sources, rag_mode

    async def stream_chat_prepared(
        self,
        req: AssistantChatRequest,
        data_ctx: str,
        rag_chunks: list[KnowledgeChunk],
        rag_mode: str,
        rag_sources: list[str],
    ) -> AsyncIterator[tuple[str, dict]]:
        """SSE 事件（上下文须在进入 StreamingResponse 前准备好）。"""
        meta = {
            "rag_sources": rag_sources,
            "rag_mode": rag_mode,
        }

        if settings.LLM_API_KEY and settings.LLM_BASE_URL:
            try:
                yield "meta", {**meta, "mode": "llm"}
                stream = self._llm_stream(req, data_ctx, rag_chunks)
                async for chunk in self._batched_text_stream(stream):
                    yield "delta", {"content": chunk}
                yield "done", {}
                return
            except Exception:
                pass

        reply = self._rule_reply(req, data_ctx, rag_chunks)
        yield "meta", {**meta, "mode": "rule"}
        async for chunk in self._batched_text_stream(self._stream_text_chunks(reply)):
            yield "delta", {"content": chunk}
        yield "done", {}

    async def stream_chat(
        self,
        conn: pymysql.connections.Connection,
        req: AssistantChatRequest,
    ) -> AsyncIterator[tuple[str, dict]]:
        data_ctx = self.build_data_context(conn)
        rag_chunks, rag_mode = self.retrieve_context(req.message)
        rag_sources = [c.citation for c in rag_chunks]
        async for item in self.stream_chat_prepared(
            req, data_ctx, rag_chunks, rag_mode, rag_sources
        ):
            yield item

    async def _llm_stream(
        self,
        req: AssistantChatRequest,
        data_ctx: str,
        rag_chunks: list[KnowledgeChunk],
    ) -> AsyncIterator[str]:
        messages = self._build_messages(req, data_ctx, rag_chunks)
        payload = {
            "model": settings.LLM_MODEL,
            "messages": messages,
            "temperature": 0.35,
            "max_tokens": 1200,
            "stream": True,
        }
        timeout = httpx.Timeout(settings.LLM_TIMEOUT_SECONDS, connect=30.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            async with client.stream(
                "POST",
                self._llm_url(),
                headers=self._llm_headers(),
                json=payload,
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line or not line.startswith("data: "):
                        continue
                    data = line[6:].strip()
                    if data == "[DONE]":
                        break
                    try:
                        body = json.loads(data)
                    except json.JSONDecodeError:
                        continue
                    choice = body.get("choices", [{}])[0]
                    delta = choice.get("delta", {})
                    content = delta.get("content")
                    if content:
                        yield str(content)

    async def _batched_text_stream(
        self,
        source: AsyncIterator[str],
        *,
        min_chars: int = 16,
        max_wait: float = 0.035,
    ) -> AsyncIterator[str]:
        """合并细碎 token，降低 SSE 事件频率。"""
        parts: list[str] = []
        last_flush = time.monotonic()

        async for chunk in source:
            parts.append(chunk)
            buf = "".join(parts)
            now = time.monotonic()
            if len(buf) >= min_chars or (now - last_flush) >= max_wait:
                yield buf
                parts.clear()
                last_flush = now

        if parts:
            yield "".join(parts)

    async def _stream_text_chunks(self, text: str, size: int = 24) -> AsyncIterator[str]:
        for i in range(0, len(text), size):
            yield text[i : i + size]
            await asyncio.sleep(0.002)

    async def _llm_chat(
        self,
        req: AssistantChatRequest,
        data_ctx: str,
        rag_chunks: list[KnowledgeChunk],
    ) -> str:
        messages = self._build_messages(req, data_ctx, rag_chunks)
        payload = {
            "model": settings.LLM_MODEL,
            "messages": messages,
            "temperature": 0.35,
            "max_tokens": 1200,
        }
        async with httpx.AsyncClient(timeout=settings.LLM_TIMEOUT_SECONDS) as client:
            res = await client.post(
                self._llm_url(),
                headers=self._llm_headers(),
                json=payload,
            )
            res.raise_for_status()
            body = res.json()
        return str(body["choices"][0]["message"]["content"]).strip()

    def _rule_reply(
        self,
        req: AssistantChatRequest,
        data_ctx: str,
        rag_chunks: list[KnowledgeChunk],
    ) -> str:
        q = req.message.lower()
        nav = _NAV_EN if req.locale == "en" else _NAV_ZH
        en = req.locale == "en"

        rag_text = "\n\n".join(c.as_context_block() for c in rag_chunks[:3])
        rag_header = "Related docs:\n" if en else "相关文档摘录：\n"

        def route_hint(keys: list[str]) -> str:
            hits = [f"{p} ({nav[p]})" for p in keys if p in nav]
            return "; ".join(hits) if hits else ""

        if re.search(r"soc|电量|remaining", q):
            hint = route_hint(["/bda2", "/predict/soc"])
            return f"{rag_header}{rag_text}\n\n{data_ctx}\n\n" + (
                f"SOC: {hint}." if en else f"SOC 相关：{hint}。"
            )
        if re.search(r"rate|速率|speed|current", q):
            hint = route_hint(["/bda4"])
            return f"{rag_header}{rag_text}\n\n{data_ctx}\n\n" + (
                f"Charging rate: {hint}." if en else f"充电速率：{hint}。"
            )
        if re.search(r"time|时间|daily|每日|次数|session|充电", q):
            hint = route_hint(["/bda1", "/bda3"])
            return f"{rag_header}{rag_text}\n\n{data_ctx}\n\n" + (
                f"Charging time/frequency: {hint}." if en else f"充电时间/次数：{hint}。"
            )
        if re.search(r"predict|预测|ml|模型|fee|费用|platform|平台", q):
            hint = route_hint(["/predict/soc", "/predict/duration", "/predict/fee", "/predict/platform"])
            return f"{rag_header}{rag_text}\n\n{data_ctx}\n\n" + (
                f"ML pages: {hint}." if en else f"预测页面：{hint}。"
            )
        if re.search(r"bi|大屏|可视化|dashboard|chart|图", q):
            hint = route_hint(["/mr-bi"])
            return f"{rag_header}{rag_text}\n\n{data_ctx}\n\n" + (
                f"Dashboard: {hint}." if en else f"BI 大屏：{hint}。"
            )
        if re.search(r"nav|菜单|去哪|where|page|路由", q):
            return self._nav_text(req.locale) + f"\n\n{rag_header}{rag_text}\n\n{data_ctx}"

        prefix = (
            "(LLM unavailable — showing RAG excerpts)\n\n"
            if en
            else "（大模型暂不可用，以下为 RAG 检索摘录）\n\n"
        )
        return prefix + f"{rag_header}{rag_text}\n\n{data_ctx}\n\n{self._nav_text(req.locale)}"
