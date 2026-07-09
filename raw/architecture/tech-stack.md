---
type: architecture
title: "Tech Stack"
date_created: 2025-05-22
date_updated: 2026-05-22
tags: [product/architecture]
---

# [PRODUCTION] Tech Stack

## FREE / LOCAL AI STACK
- **Embeddings:** BAAI/bge-small-en-v1.5
- **Primary LLM:** Qwen2.5-Coder:7B via Ollama
- **Fallback LLMs:** Mistral, Phi-3
- **Vector Search:** pgvector
- **Database:** PostgreSQL (Supabase)

## AI Responsibility Rule

Math decides. AI explains.

- The embedding model powers semantic similarity and vector search.
- The deterministic hybrid scoring engine ranks candidates.
- Qwen2.5-Coder:7B generates summaries, explanations, recruiter insights, and interview questions.
- The LLM cannot override scores, reorder candidates, alter the hybrid score, or make hiring decisions.

## Backend
- Django, Django REST Framework
- Celery, Redis

## Frontend
- Next.js, TypeScript, TailwindCSS

## Deployment
- Nginx
- Gunicorn
- Django

## Storage
- Supabase Storage (Cheaper, easier, better for MVP than AWS S3)

## Related Documents

- [[ai-responsibilities|AI Responsibilities]]
- [[ai-pipeline|AI Pipeline]]
- [[semantic-matching|Semantic Matching]]
