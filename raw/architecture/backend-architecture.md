---
type: architecture
title: "Backend Architecture"
date_created: 2025-05-22
date_updated: 2026-05-22
tags: [product/architecture, backend/django, backend/drf]
---

# Backend Architecture

## Overview

The backend is built with **Django 5.x** and **Django REST Framework (DRF)**, following a modular app-based architecture. Each domain concern is isolated into its own Django app with clear boundaries, serializers, views, and permissions. The API is versioned under `/api/v1/` and designed for consumption by the Next.js frontend as well as potential third-party integrations.

---

## Django Project Structure

```
backend/
├── config/                    # Project configuration
│   ├── settings/
│   │   ├── base.py            # Shared settings
│   │   ├── development.py     # Local dev overrides
│   │   ├── staging.py         # Staging environment
│   │   └── production.py      # Production settings
│   ├── urls.py                # Root URL configuration
│   ├── wsgi.py                # WSGI application
│   ├── celery.py              # Celery app configuration
│   └── asgi.py                # ASGI application (future WebSocket support)
│
├── apps/
│   ├── accounts/              # User management & authentication
│   ├── organizations/         # Multi-tenant organization management
│   ├── jobs/                  # Job postings & requirements
│   ├── candidates/            # Candidate profiles & applications
│   ├── ai_engine/             # AI pipeline (parsing, scoring, insights)
│   ├── pipeline/              # Hiring pipeline & stage management
│   ├── analytics/             # Reporting & metrics
│   └── notifications/         # Email & in-app notifications
│
├── common/                    # Shared utilities
│   ├── permissions.py         # Custom DRF permission classes
│   ├── pagination.py          # Standardized pagination
│   ├── mixins.py              # Reusable view mixins
│   ├── exceptions.py          # Custom exception handlers
│   └── middleware.py          # Organization-scoping middleware
│
├── manage.py
├── requirements.txt
└── Dockerfile
```

---

## App Organization

Each app follows a consistent internal structure:

```
apps/candidates/
├── __init__.py
├── models.py                  # Django ORM models
├── serializers.py             # DRF serializers (input validation + output formatting)
├── views.py                   # DRF ViewSets and APIViews
├── urls.py                    # App-level URL patterns
├── filters.py                 # Django-filter FilterSet definitions
├── signals.py                 # Post-save/delete signals (e.g., trigger AI pipeline)
├── tasks.py                   # Celery task definitions
├── services.py                # Business logic layer (keep views thin)
├── tests/
│   ├── test_models.py
│   ├── test_serializers.py
│   ├── test_views.py
│   └── test_services.py
├── admin.py                   # Django admin configuration
└── migrations/
```

### App Responsibilities

| App               | Responsibility                                              | Key Models                                            |
| ----------------- | ----------------------------------------------------------- | ----------------------------------------------------- |
| **accounts**      | User registration, login, password management, profile      | `User`, `UserProfile`                                 |
| **organizations** | Org CRUD, membership management, settings                   | `Organization`, `Membership`                          |
| **jobs**          | Job posting CRUD, skill requirements, status management     | `Job`, `JobSkill`                                     |
| **candidates**    | Candidate profiles, resume upload, application tracking     | `Candidate`, `CandidateApplication`, `CandidateScore` |
| **ai_engine**     | Resume parsing, embedding generation, scoring, LLM insights | `AITask`, `EmbeddingCache`                            |
| **pipeline**      | Hiring stages, candidate progression, interview feedback    | `PipelineStage`, `StageHistory`, `Feedback`           |
| **analytics**     | Dashboard metrics, report generation, data aggregation      | `MetricSnapshot`                                      |
| **notifications** | Email dispatch, in-app notification center, preferences     | `Notification`, `NotificationPreference`              |

---

## DRF Serializer Patterns

### Input vs Output Serializers

We separate input (write) and output (read) serializers to decouple validation from representation:

```python
class CandidateApplicationCreateSerializer(serializers.Serializer):
    """Validates a candidate profile plus job application request."""
    full_name = serializers.CharField()
    email = serializers.EmailField()
    phone = serializers.CharField(required=False, allow_blank=True)
    resume = serializers.FileField(required=True)
    job_id = serializers.UUIDField()
    source = serializers.ChoiceField(choices=['direct', 'referral', 'linkedin', 'agency'], required=False)

class CandidateApplicationDetailSerializer(serializers.ModelSerializer):
    """Job-specific application state for a candidate."""
    score = CandidateScoreSerializer(read_only=True)
    parsed_data = serializers.JSONField(read_only=True)

    class Meta:
        model = CandidateApplication
        fields = ['id', 'job', 'current_stage', 'status', 'source', 'score']

class CandidateDetailSerializer(serializers.ModelSerializer):
    """Rich profile representation with nested application data."""
    applications = CandidateApplicationDetailSerializer(many=True, read_only=True)
    parsed_data = serializers.JSONField(read_only=True)

    class Meta:
        model = Candidate
        fields = ['id', 'full_name', 'email', 'phone', 'resume_url',
                  'parsed_data', 'applications', 'created_at', 'updated_at']
```

### Nested Serializers

For related data, we use nested serializers for read operations and PrimaryKeyRelatedField for writes:

```python
class JobDetailSerializer(serializers.ModelSerializer):
    skills = JobSkillSerializer(many=True, read_only=True)
    candidate_count = serializers.IntegerField(read_only=True)
    created_by = UserMinimalSerializer(read_only=True)
```

---

## Permission Classes

All permissions enforce organization-scoped access:

```python
class IsOrgMember(BasePermission):
    """Allows any member of the organization."""
    def has_permission(self, request, view):
        return hasattr(request.user, 'org_id') and request.user.org_id is not None

class IsOrgAdmin(BasePermission):
    """Restricts to organization administrators."""
    def has_permission(self, request, view):
        return request.user.role == 'admin'

class IsOrgRecruiter(BasePermission):
    """Allows admins and recruiters."""
    def has_permission(self, request, view):
        return request.user.role in ['admin', 'recruiter']

class IsOwnerOrAdmin(BasePermission):
    """Object-level: only the creator or an admin can modify."""
    def has_object_permission(self, request, view, obj):
        return obj.created_by == request.user or request.user.role == 'admin'
```

---

## Database Query Optimization

### Organization Scoping Mixin

Every queryset is automatically scoped by organization:

```python
class OrgScopedMixin:
    def get_queryset(self):
        return super().get_queryset().filter(
            organization_id=self.request.user.org_id
        )
```

### Common Optimization Patterns

| Pattern | When to Use | Example |
|---------|------------|---------|
| `select_related()` | ForeignKey lookups | `CandidateApplication.objects.select_related('candidate', 'job', 'current_stage')` |
| `prefetch_related()` | Reverse FK / M2M | `Job.objects.prefetch_related('skills', 'candidate_applications')` |
| `only()` / `defer()` | Large fields not needed | `Candidate.objects.defer('parsed_data', 'embedding')` |
| `annotate()` + `Count` | Aggregation in list views | `Job.objects.annotate(application_count=Count('candidate_applications'))` |
| `Subquery` | Complex filtered counts | Active candidates per stage |

### N+1 Prevention

All ViewSets that return nested data must use `select_related` and `prefetch_related` in `get_queryset()`. The Django Debug Toolbar is enabled in development to catch N+1 query patterns.

---

## Celery Task Organization

Tasks are defined within each app's `tasks.py` and registered with specific queues:

```python
# apps/ai_engine/tasks.py
@shared_task(
    bind=True,
    queue='ai',
    max_retries=3,
    retry_backoff=True,
    rate_limit='10/m',
)
def parse_resume(self, candidate_id: str):
    """Extract and parse resume content."""
    ...

@shared_task(queue='ai', max_retries=3)
def generate_embedding(self, candidate_id: str):
    """Generate embedding vector for candidate."""
    ...

@shared_task(queue='scoring', max_retries=2)
def compute_scores(self, application_id: str):
    """Run hybrid scoring pipeline for a job-specific application."""
    ...

@shared_task(queue='default')
def send_notification(self, notification_id: str):
    """Dispatch email or in-app notification."""
    ...
```

See [[async-task-flow|Async Task Flow]] for queue configuration, priorities, and monitoring.

---

## API Versioning

```python
# config/urls.py
urlpatterns = [
    path('api/v1/auth/', include('apps.accounts.urls')),
    path('api/v1/organizations/', include('apps.organizations.urls')),
    path('api/v1/jobs/', include('apps.jobs.urls')),
    path('api/v1/candidates/', include('apps.candidates.urls')),
    path('api/v1/pipeline/', include('apps.pipeline.urls')),
    path('api/v1/analytics/', include('apps.analytics.urls')),
    path('api/v1/ai/', include('apps.ai_engine.urls')),
]
```

---

## Related Documents

- [[system-overview|System Overview]] — High-level platform architecture and stack decisions.
- [[auth-api|Authentication API]] — Authentication endpoint reference.
- [[jobs-api|Jobs API]] — Job posting API endpoints and request/response schemas.
- [[candidate-api|Candidate API]] — Candidate management API endpoints.
- [[pipeline-api|Pipeline API]] — Pipeline stage management API endpoints.
- [[ai-api|AI API]] — AI engine API endpoints (parsing, scoring, insights).
- [[async-task-flow|Async Task Flow]] — Celery configuration, queues, and monitoring.
