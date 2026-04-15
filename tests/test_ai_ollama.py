"""Unit tests for Ollama integration (model missing, etc.)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import httpx
import pytest

from examai.integration.ai import OllamaClientError, ollama_generate


def _mock_client_cm(mock_client: MagicMock) -> MagicMock:
    cm = MagicMock()
    cm.__enter__.return_value = mock_client
    cm.__exit__.return_value = False
    return cm


def test_ollama_generate_model_not_found_404_friendly_message() -> None:
    req = httpx.Request("POST", "http://ollama.test/api/generate")
    resp = httpx.Response(
        404,
        json={"error": "model 'deepseek-r1:8b' not found"},
        request=req,
    )
    mock_client = MagicMock()
    mock_client.post.return_value = resp

    with patch("examai.integration.ai.httpx.Client", return_value=_mock_client_cm(mock_client)):
        with pytest.raises(OllamaClientError) as excinfo:
            ollama_generate(
                base_url="http://ollama.test",
                model="deepseek-r1:8b",
                prompt="hello",
                timeout_seconds=30.0,
                max_retries=1,
            )
    msg = str(excinfo.value)
    assert "not available in Ollama" in msg
    assert "ollama pull" in msg
    assert "OLLAMA_MODEL" in msg
    assert "HTTP 404" not in msg


def test_ollama_generate_other_http_error_still_includes_status() -> None:
    req = httpx.Request("POST", "http://ollama.test/api/generate")
    resp = httpx.Response(500, json={"error": "internal"}, request=req)
    mock_client = MagicMock()
    mock_client.post.return_value = resp

    with patch("examai.integration.ai.httpx.Client", return_value=_mock_client_cm(mock_client)):
        with pytest.raises(OllamaClientError) as excinfo:
            ollama_generate(
                base_url="http://ollama.test",
                model="llama3.2",
                prompt="hello",
                timeout_seconds=30.0,
                max_retries=1,
            )
    assert "HTTP 500" in str(excinfo.value)
