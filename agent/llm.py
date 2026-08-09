"""
CivicPulse — LLM provider wrapper: Databricks Foundation Model API.

Everything the agent needs (chat + tool-calling, embeddings, one-off
summarization) is served natively by the workspace's Foundation Model API --
pay-per-token, included in Free Edition, no external provider, no external
API key, no credit card anywhere in the stack.

Both chat and embeddings go through the same mechanism: an OpenAI-compatible
client obtained from `WorkspaceClient().serving_endpoints.get_open_ai_client()`.
Inside Databricks (notebook, Job, or Databricks App) this client authenticates
automatically using the attached compute's own credentials -- no token
handling in this file. Locally, the Databricks SDK falls back to your
`databricks auth login` profile or DATABRICKS_HOST/DATABRICKS_TOKEN env vars.

This module is the single seam that knows which model serves the agent --
agent.py, tools.py, and the jobs only ever call the functions below, never a
provider client directly, so swapping FOUNDATION_MODEL_CHAT (or EMBEDDING_MODEL,
in config/settings.py) touches nothing else.
"""

from __future__ import annotations

import json

from config.settings import EMBEDDING_MODEL, FOUNDATION_MODEL_CHAT

_client = None


def _openai_client():
    """Lazily build (and cache) the OpenAI-compatible client for Foundation Model API calls."""
    global _client
    if _client is None:
        from databricks.sdk import WorkspaceClient

        _client = WorkspaceClient().serving_endpoints.get_open_ai_client()
    return _client


def chat_completion(
    messages: list[dict],
    tools: list[dict] | None = None,
    temperature: float = 0.2,
) -> dict:
    """
    Single-turn chat call against the Foundation Model API, normalized to an
    {"text": ..., "tool_calls": [...]} shape so agent.py doesn't need to know
    the underlying response format.

    `messages` is already OpenAI-shaped ({"role", "content"}), and so are
    `tools` once wrapped in the {"type": "function", "function": {...}}
    envelope below -- the Foundation Model API's chat endpoints are
    OpenAI-compatible, so no message-format translation is needed the way a
    non-OpenAI-shaped provider would require.

    Kept deliberately low-temperature (strategy doc section 18: "keep
    temperature low for agent calls") so the scripted demo conversations are
    reproducible.
    """
    client = _openai_client()

    kwargs: dict = {
        "model": FOUNDATION_MODEL_CHAT,
        "messages": messages,
        "temperature": temperature,
    }
    if tools:
        kwargs["tools"] = [{"type": "function", "function": t} for t in tools]
        kwargs["tool_choice"] = "auto"

    response = client.chat.completions.create(**kwargs)
    choice = response.choices[0]

    tool_calls = []
    for call in getattr(choice.message, "tool_calls", None) or []:
        tool_calls.append({
            "name": call.function.name,
            "arguments": call.function.arguments,  # JSON string; parse_tool_call_args() handles it
        })

    return {"text": choice.message.content or "", "tool_calls": tool_calls}


def embed_texts(texts: list[str], model: str = EMBEDDING_MODEL) -> list[list[float]]:
    """
    Embed a batch of chunk texts via the Foundation Model API
    (databricks-gte-large-en, 1024-dim -- the model Phase 1 wired the AI
    Search index to. This must stay in sync with that index definition or
    writes will be rejected).
    """
    client = _openai_client()
    response = client.embeddings.create(model=model, input=texts)
    return [item.embedding for item in response.data]


def generate_summary(title: str, full_text: str) -> str:
    """One-time plain-language summary generation, cached by embed_chunks.py into gold_bill_summary."""
    prompt = (
        "Summarize the following legislative bill in 2-3 plain-language sentences "
        "a non-lawyer resident would understand. Do not invent details not present "
        "in the text.\n\n"
        f"Title: {title}\n\nText: {full_text[:6000]}"
    )
    result = chat_completion([{"role": "user", "content": prompt}])
    return result["text"].strip()


def parse_tool_call_args(raw_args) -> dict:
    """Defensive parsing -- tool-call args come back as a JSON string, not a dict."""
    if isinstance(raw_args, dict):
        return raw_args
    return json.loads(raw_args)
