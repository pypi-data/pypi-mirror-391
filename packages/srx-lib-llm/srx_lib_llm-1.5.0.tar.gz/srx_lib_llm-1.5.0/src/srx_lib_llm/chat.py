import os
import openai
from langchain_core.globals import set_llm_cache
from langchain_community.cache import InMemoryCache
from langchain_openai import ChatOpenAI

from .instrumentation import get_langfuse_handler


async def responses_chat(question: str, cache: bool = False) -> str:
    """Single-turn chat using LangChain's ChatOpenAI Responses API.

    Uses official OpenAI only via:
    - OPENAI_API_KEY
    - Optional: OPENAI_MODEL (default: gpt-4.1-nano)
    """
    if cache:
        set_llm_cache(InMemoryCache())
    else:
        set_llm_cache(None)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY must be set")
    openai.api_key = api_key
    langfuse_handler = get_langfuse_handler()
    callbacks = [langfuse_handler] if langfuse_handler else None
    llm = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4.1-nano"),
        use_responses_api=True,
        output_version="responses/v1",
        api_key=api_key,
        temperature=0.7,
        callbacks=callbacks,
    )

    config = {"callbacks": callbacks} if callbacks else None
    msg = await llm.ainvoke(question, config=config)
    content = getattr(msg, "content", msg)
    if isinstance(content, list):
        try:
            return "".join(
                part.get("text", "")
                for part in content
                if isinstance(part, dict) and part.get("type") == "text"
            )
        except Exception:
            return ""
    if isinstance(content, str):
        return content
    try:
        text_attr = getattr(msg, "text", None)
        if callable(text_attr):
            return text_attr() or ""
    except Exception:
        pass
    return str(content) if content is not None else ""
