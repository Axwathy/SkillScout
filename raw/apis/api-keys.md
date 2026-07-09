---
type: api
title: "API Keys"
date_created: 2026-05-22
date_updated: 2026-05-22
tags: [product/architecture, security/secrets]
---

# [PRODUCTION] API Keys

Do not store live API keys in the vault or repository.

## Required Action

A plaintext Ollama-related key was previously stored in this file. Treat it as exposed and rotate it before using the service in any shared or production environment.

## Secret Management Rule

- Store local secrets in `.env` files excluded by `.gitignore`.
- Store staging/production secrets in the deployment platform secret manager.
- Reference secrets in documentation by environment variable name only.

## Environment Variables

| Variable | Purpose |
|---|---|
| `OLLAMA_BASE_URL` | Ollama endpoint |
| `LLM_MODEL` | Primary local LLM, default `qwen2.5-coder:7b` |
| `LLM_FALLBACK_MODELS` | Fallback local LLMs, default `mistral,phi3` |
| `EMBEDDING_MODEL` | Embedding model, default `BAAI/bge-small-en-v1.5` |
| `EMBEDDING_DIMENSIONS` | Embedding dimension, default `384` |
