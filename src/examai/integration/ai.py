"""Ollama HTTP client (httpx, bounded timeouts) — docs/development-guide.md."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import httpx


class OllamaClientError(Exception):
    """LLM request failed (network, timeout, or API error)."""


@dataclass(frozen=True)
class OllamaGenerateResult:
    """Parsed /api/generate response."""

    text: str
    model_name: str
    model_version: str | None


def _parse_generate_json(payload: dict[str, Any]) -> tuple[str, str, str | None]:
    if payload.get("error"):
        raise OllamaClientError(str(payload["error"]))
    text = payload.get("response")
    if not isinstance(text, str):
        raise OllamaClientError("Ollama response missing 'response' text.")
    model = payload.get("model")
    model_name = model if isinstance(model, str) else ""
    version = payload.get("version")
    mv = version if isinstance(version, str) else None
    return text, model_name, mv


def ollama_generate(
    *,
    base_url: str,
    model: str,
    prompt: str,
    timeout_seconds: float,
    max_retries: int,
) -> OllamaGenerateResult:
    """
    POST /api/generate with stream=false.

    Retries only on transport errors (connection, read timeout), not on HTTP 4xx/5xx bodies.
    """
    root = base_url.rstrip("/")
    url = f"{root}/api/generate"
    body = {"model": model, "prompt": prompt, "stream": False}
    timeout = httpx.Timeout(timeout_seconds, connect=min(10.0, timeout_seconds))
    attempts = max(1, min(max_retries, 5))
    for attempt in range(attempts):
        try:
            with httpx.Client(timeout=timeout) as client:
                r = client.post(url, json=body)
                r.raise_for_status()
                payload = r.json()
        except httpx.HTTPStatusError as e:
            detail = ""
            try:
                detail = e.response.text[:500]
            except Exception:
                pass
            raise OllamaClientError(f"HTTP {e.response.status_code} from Ollama. {detail}") from e
        except (httpx.TransportError, httpx.TimeoutException, json.JSONDecodeError) as e:
            if attempt + 1 >= attempts:
                raise OllamaClientError(f"Ollama request failed after {attempts} attempt(s).") from e
            continue
        except OllamaClientError:
            raise
        except Exception as e:
            raise OllamaClientError("Unexpected error talking to Ollama.") from e

        text, resp_model, model_version = _parse_generate_json(payload)
        model_name = resp_model if resp_model else model
        return OllamaGenerateResult(text=text, model_name=model_name, model_version=model_version)

    raise OllamaClientError("Ollama request failed.")
