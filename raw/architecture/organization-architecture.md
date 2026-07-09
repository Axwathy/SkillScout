---
type: architecture
title: "Organization Architecture and Multi-Tenant Design"
date_created: 2026-05-30
date_updated: 2026-05-30
sprint_implemented: 2
tags: [product/architecture, product/strategy]
related_adr: "ADR-006-multi-tenant"
---

# Organization Architecture

## The Organization as Tenant Boundary

Every piece of data in the platform belongs to an Organization. The Organization is the top-level entity:

```
Organization
├── Recruiters (users who work here)
├── Jobs (Sprint 3+)
├── Candidates (Sprint 3+)
├── Applications (Sprint 3+)
└── Pipeline Stages (Sprint 3+)
```

Cross-organization data access is prohibited at every layer.

## Model Definition (Sprint 2)

```python
class Organization(models.Model):
    id               = UUIDField(primary_key=True)
    name             = CharField(max_length=255)
    slug             = SlugField(unique=True)
    website          = URLField(blank=True)
    approval_status  = CharField(choices=["pending","approved","rejected","suspended"])
    is_active        = BooleanField(default=True)
    created_at       = DateTimeField
    updated_at       = DateTimeField
```

## Approval Flow

Organizations must be approved by an admin before their recruiters can login:

1. Registration creates org with `approval_status=pending`
2. Admin reviews at `/dashboard/admin/organizations`
3. Admin approves → `approval_status=approved`
4. Recruiter of that org can now complete login

## Future Organization Fields (Sprint 4+)

- `subscription_tier` — free/starter/growth/enterprise
- `max_recruiters` — seat limit
- `custom_domain` — white-label support
- `branding` — logo, colors
- `settings` — JSONField for org-level config

## Tenant Isolation Pattern (Sprint 3+)

All tenant-owned models will use `OrganizationScopedQuerySet`:

```python
class OrganizationScopedQuerySet(models.QuerySet):
    def for_org(self, organization):
        return self.filter(organization=organization)

class OrganizationScopedManager(models.Manager):
    def get_queryset(self):
        return OrganizationScopedQuerySet(self.model, using=self._db)
```

Views use:
```python
queryset = Job.objects.for_org(request.user.recruiter_profile.organization)
```

Serializers set organization from user, never from request data:
```python
def perform_create(self, serializer):
    serializer.save(organization=self.request.user.recruiter_profile.organization)
```

## Slug Generation

Slugs are auto-generated from `name` on first save using `django.utils.text.slugify`. Collisions get a numeric suffix (`acme-corp-2`). Slug is immutable after creation.
