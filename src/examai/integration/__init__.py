"""External integrations (Git, Ollama, etc.) — keep HTTP clients out of route handlers."""

from examai.integration.ai import OllamaClientError, ollama_generate

__all__ = ["OllamaClientError", "ollama_generate"]
