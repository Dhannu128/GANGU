"""
GANGU shared LLM client.

Drop-in shim that mirrors the surface of `google.genai.Client` used by the
agents but routes every call to TokenRouter's OpenAI-compatible chat
completions endpoint. This lets us swap Gemini for Claude (or any other
TokenRouter-served model) by changing one import line per agent.

Each agent does:
    from agents import llm as genai
    client = genai.Client()
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=chat_history,
        config={"temperature": 0.2, "max_output_tokens": 8192, ...},
    )
    text = response.text

The shim translates Gemini-flavoured arguments to OpenAI ones:
  - role "model"            -> "assistant"
  - parts: [{"text": ...}]  -> content: "..."
  - max_output_tokens       -> max_tokens
  - response_mime_type      -> response_format={"type": "json_object"}
  - top_k                   -> dropped (no OpenAI equivalent)
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Iterable

from dotenv import load_dotenv
from openai import OpenAI

try:
    from langsmith.wrappers import wrap_openai  # auto-traces every call
except ImportError:  # pragma: no cover — langsmith is optional
    wrap_openai = None  # type: ignore[assignment]

# Load .env from project root, then from cwd (matches what every agent does).
_GANGU_ROOT = Path(__file__).parent.parent
load_dotenv(dotenv_path=_GANGU_ROOT / ".env")
load_dotenv()

DEFAULT_BASE_URL = "https://api.tokenrouter.com/v1"
DEFAULT_MODEL = "claude-haiku-4-5"


def get_model_name() -> str:
    """Resolve the model id from env, falling back to Claude Haiku 4.5."""
    return os.environ.get("LLM_MODEL", DEFAULT_MODEL)


def _build_openai_client() -> OpenAI:
    api_key = os.environ.get("TOKENROUTER_API_KEY")
    if not api_key:
        raise ValueError(
            "TOKENROUTER_API_KEY environment variable not set. "
            "Add it to .env (see .env.example)."
        )
    base_url = os.environ.get("TOKENROUTER_BASE_URL", DEFAULT_BASE_URL)
    client = OpenAI(api_key=api_key, base_url=base_url)
    # Auto-trace every chat completion to LangSmith when tracing is on.
    if wrap_openai is not None and os.environ.get("LANGSMITH_TRACING", "").lower() == "true":
        try:
            client = wrap_openai(client)
        except Exception:  # never let tracing setup break the agents
            pass
    return client


class _Response:
    """Mimics the subset of google.genai response object the agents read."""

    def __init__(self, text: str):
        self.text = text


def _convert_contents(contents: Iterable[dict[str, Any]] | None) -> list[dict[str, str]]:
    """Translate Gemini-style chat_history into OpenAI messages."""
    if not contents:
        return []

    messages: list[dict[str, str]] = []
    for entry in contents:
        if not isinstance(entry, dict):
            continue
        role = entry.get("role", "user")
        parts = entry.get("parts", [])
        if isinstance(parts, str):
            text = parts
        else:
            text = "".join(
                part.get("text", "") if isinstance(part, dict) else str(part)
                for part in parts
            )
        if role == "model":
            role = "assistant"
        elif role not in ("user", "system", "assistant"):
            role = "user"
        messages.append({"role": role, "content": text})
    return messages


def _convert_config(config: dict[str, Any] | None) -> dict[str, Any]:
    """Translate Gemini generate_content config into OpenAI kwargs."""
    if not config:
        return {}

    kwargs: dict[str, Any] = {}
    if "temperature" in config:
        kwargs["temperature"] = config["temperature"]
    if "top_p" in config:
        kwargs["top_p"] = config["top_p"]
    if "max_output_tokens" in config:
        kwargs["max_tokens"] = config["max_output_tokens"]
    elif "max_tokens" in config:
        kwargs["max_tokens"] = config["max_tokens"]
    if config.get("response_mime_type") == "application/json":
        kwargs["response_format"] = {"type": "json_object"}
    if "response_format" in config:
        kwargs["response_format"] = config["response_format"]
    # top_k has no OpenAI equivalent; silently drop.
    return kwargs


class _ModelsAPI:
    """Mirrors `client.models.generate_content(...)` from google.genai."""

    def __init__(self, openai_client: OpenAI):
        self._client = openai_client

    def generate_content(
        self,
        model: str | None = None,
        contents: Iterable[dict[str, Any]] | None = None,
        config: dict[str, Any] | None = None,
    ) -> _Response:
        messages = _convert_contents(contents)
        kwargs = _convert_config(config)
        chosen_model = model or get_model_name()
        # If an agent still hands us a Gemini model name, fall back to env.
        if chosen_model.lower().startswith("gemini"):
            chosen_model = get_model_name()

        completion = self._client.chat.completions.create(
            model=chosen_model,
            messages=messages,
            **kwargs,
        )
        text = completion.choices[0].message.content or ""
        return _Response(text)


class Client:
    """Drop-in replacement for `google.genai.Client`."""

    def __init__(self, api_key: str | None = None):
        # api_key arg is ignored (kept for signature compatibility).
        # The real key comes from TOKENROUTER_API_KEY in the environment.
        del api_key
        self._openai = _build_openai_client()
        self.models = _ModelsAPI(self._openai)
