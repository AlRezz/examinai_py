#!/bin/sh
# Used by docker-compose `llm` service: start Ollama, then ensure OLLAMA_PULL_MODEL is present.
# First pull can take a long time; repeats are fast when the tag already exists.
set -eu

MODEL="${OLLAMA_PULL_MODEL:-}"

ollama serve &
pid=$!

i=0
while [ "$i" -lt 120 ]; do
  if ollama list >/dev/null 2>&1; then
    break
  fi
  i=$((i + 1))
  sleep 1
done

if ! ollama list >/dev/null 2>&1; then
  echo "ollama-compose: server did not become ready in time" >&2
  exit 1
fi

if [ -n "$MODEL" ]; then
  echo "ollama-compose: pulling model (if missing): ${MODEL}"
  ollama pull "$MODEL" || echo "ollama-compose: pull failed — check network/tag; set OLLAMA_MODEL or run: docker compose exec llm ollama pull ${MODEL}" >&2
fi

wait "$pid"
