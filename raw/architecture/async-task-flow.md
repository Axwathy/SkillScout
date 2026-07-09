---
type: architecture
title: "Async Task Flow"
date_created: 2025-05-22
date_updated: 2026-05-22
tags: [product/architecture, backend/celery, backend/redis, async]
---

# Async Task Flow

## Overview

The platform uses **Celery** with a **Redis** broker to handle asynchronous task processing. All computationally expensive or I/O-bound operations — resume parsing, embedding generation, AI scoring, email dispatch — are offloaded to background workers. This keeps the API responsive (< 200ms p95 for all synchronous endpoints) while enabling complex AI pipelines to run without blocking user interactions.

---

## Celery + Redis Architecture

```
┌──────────────┐    Task dispatch    ┌───────────────┐
│  Django API  │ ──────────────────→ │     Redis     │
│  (Producer)  │                     │   (Broker)    │
└──────────────┘                     └───────┬───────┘
                                             │
                          ┌──────────────────┼──────────────────┐
                          ▼                  ▼                  ▼
                   ┌────────────┐    ┌────────────┐    ┌────────────┐
                   │  Worker 1  │    │  Worker 2  │    │  Worker 3  │
                   │  (ai)      │    │  (scoring) │    │  (default) │
                   └─────┬──────┘    └─────┬──────┘    └─────┬──────┘
                         │                 │                 │
                         ▼                 ▼                 ▼
                   ┌─────────────────────────────────────────────┐
                   │           Redis (Result Backend)            │
                   └─────────────────────────────────────────────┘
```

### Configuration

```python
# config/celery.py
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')

app = Celery('recruitment')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# config/settings/base.py
CELERY_BROKER_URL = os.environ['REDIS_URL']
CELERY_RESULT_BACKEND = os.environ['REDIS_URL']
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 300          # 5 minutes hard limit
CELERY_TASK_SOFT_TIME_LIMIT = 240     # 4 minutes soft limit
CELERY_WORKER_PREFETCH_MULTIPLIER = 1 # Fair scheduling for mixed task durations
```

---

## Task Types

### AI Tasks (Queue: `ai`)

These are the most resource-intensive tasks, involving local Ollama inference and embedding generation:

| Task | Trigger | Average Duration | Priority |
|------|---------|-----------------|----------|
| `parse_resume` | Resume upload | 5–15s | High |
| `generate_embedding` | After parsing completes | 2–5s | High |
| `generate_llm_insights` | After scoring completes | 10–30s | Medium |
| `batch_embed_candidates` | Bulk import | 30–120s | Low |

### Scoring Tasks (Queue: `scoring`)

Deterministic computation tasks that don't require external API calls:

| Task | Trigger | Average Duration | Priority |
|------|---------|-----------------|----------|
| `compute_hybrid_score` | After embedding generation or application creation | 1–3s | High |
| `recalculate_job_scores` | Job requirements updated | 5–30s | Medium |
| `batch_score_candidates` | Bulk scoring request | 10–60s | Low |

### Default Tasks (Queue: `default`)

General-purpose tasks for non-AI operations:

| Task | Trigger | Average Duration | Priority |
|------|---------|-----------------|----------|
| `send_email_notification` | Various events | 1–3s | High |
| `send_in_app_notification` | Various events | < 1s | Medium |
| `generate_analytics_snapshot` | Scheduled (daily) | 5–15s | Low |
| `cleanup_expired_tokens` | Scheduled (hourly) | 1–5s | Low |
| `export_candidates_csv` | User request | 5–30s | Medium |

---

## Task Priorities and Queues

### Queue Configuration

```python
CELERY_TASK_QUEUES = {
    'ai': {
        'exchange': 'ai',
        'routing_key': 'ai',
    },
    'scoring': {
        'exchange': 'scoring',
        'routing_key': 'scoring',
    },
    'default': {
        'exchange': 'default',
        'routing_key': 'default',
    },
}

CELERY_TASK_ROUTES = {
    'apps.ai_engine.tasks.parse_resume': {'queue': 'ai'},
    'apps.ai_engine.tasks.generate_embedding': {'queue': 'ai'},
    'apps.ai_engine.tasks.generate_llm_insights': {'queue': 'ai'},
    'apps.candidates.tasks.compute_hybrid_score': {'queue': 'scoring'},
    'apps.notifications.tasks.*': {'queue': 'default'},
}
```

### Worker Deployment

```bash
# AI worker (2 concurrency — local model throughput)
celery -A config worker -Q ai -c 2 --hostname=ai@%h

# Scoring worker (4 concurrency — CPU-bound)
celery -A config worker -Q scoring -c 4 --hostname=scoring@%h

# Default worker (8 concurrency — lightweight tasks)
celery -A config worker -Q default -c 8 --hostname=default@%h

# Beat scheduler (single instance)
celery -A config beat --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

---

## Task Chaining (Pipeline Orchestration)

The AI pipeline uses Celery chains to orchestrate multi-step processing:

```python
from celery import chain

def process_candidate_application(candidate_id: str, application_id: str):
    """Orchestrate parsing, embedding, scoring, and insight generation."""
    pipeline = chain(
        parse_resume.si(candidate_id),
        generate_embedding.si(candidate_id),
        compute_hybrid_score.si(application_id),
        generate_llm_insights.si(application_id),
    )
    pipeline.apply_async()
```

The chain uses immutable signatures so each task reads the latest persisted database state rather than relying on positional return values. A failure in any task short-circuits the remaining pipeline.

---

## Retry Policies

| Task Category | Max Retries | Backoff Strategy | Exceptions |
|--------------|-------------|------------------|------------|
| AI model calls | 5 | Exponential (2^n, max 120s) | `ModelTimeoutError`, `ModelUnavailableError` |
| Scoring | 3 | Fixed (10s) | `DatabaseError` |
| Notifications | 3 | Exponential (2^n, max 60s) | `SMTPError`, `ConnectionError` |
| Default | 2 | Fixed (5s) | General exceptions |

```python
@shared_task(
    bind=True,
    max_retries=5,
    retry_backoff=True,
    retry_backoff_max=120,
    autoretry_for=(ModelTimeoutError, ModelUnavailableError),
    retry_jitter=True,
)
def parse_resume(self, candidate_id: str):
    ...
```

---

## Dead Letter Handling

Tasks that exhaust all retries are handled by a custom failure callback:

```python
@app.task_failure.connect
def handle_task_failure(sender, task_id, exception, args, kwargs, **kw):
    """Log failed tasks for manual inspection."""
    FailedTask.objects.create(
        task_id=task_id,
        task_name=sender.name,
        args=args,
        kwargs=kwargs,
        exception=str(exception),
        traceback=traceback.format_exc(),
    )
    # Notify admin via Slack
    notify_admin_slack(f"Task {sender.name} failed permanently: {exception}")
```

Failed tasks are stored in a `FailedTask` model and visible in the Django admin for manual retry or investigation.

---

## Monitoring with Flower

**Flower** provides a real-time web UI for monitoring Celery workers, tasks, and queues.

```bash
celery -A config flower --port=5555 --basic_auth=admin:password
```

### Key Metrics Monitored

| Metric | Alert Threshold | Action |
|--------|----------------|--------|
| Queue depth (ai) | > 50 tasks | Scale AI workers |
| Queue depth (scoring) | > 100 tasks | Scale scoring workers |
| Task failure rate | > 5% (5 min window) | Investigate Ollama/model service health |
| Worker heartbeat missed | > 60s | Restart worker |
| Average task duration (ai) | > 60s | Check local model latency, optimize prompts |

### Scheduled Tasks (Celery Beat)

| Task | Schedule | Purpose |
|------|----------|---------|
| `generate_analytics_snapshot` | Daily at 02:00 UTC | Pre-compute dashboard metrics |
| `cleanup_expired_tokens` | Hourly | Remove blacklisted JWT tokens from Redis |
| `cleanup_stale_tasks` | Every 6 hours | Mark hung tasks as failed |
| `send_weekly_digest` | Monday 09:00 UTC | Weekly recruitment summary email |

---

## Related Documents

- [[ai-pipeline|AI Pipeline]] — The AI processing pipeline that generates most async tasks.
- [[backend-architecture|Backend Architecture]] — Django project structure and task organization.
- [[deployment-architecture|Deployment Architecture]] — Worker deployment and scaling strategy.
- [[system-overview|System Overview]] — High-level platform architecture.
