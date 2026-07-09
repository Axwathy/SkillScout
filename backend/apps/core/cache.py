from __future__ import annotations

from hashlib import sha256
from typing import Any

from django.core.cache import cache

ORG_CACHE_VERSION_TIMEOUT = None


def get_org_cache_version(organization: Any) -> int:
    organization_id = _organization_id(organization)
    key = _org_version_key(organization_id)
    version = cache.get(key)
    if version is None:
        version = 1
        cache.set(key, version, timeout=ORG_CACHE_VERSION_TIMEOUT)
    return int(version)


def invalidate_org_cache(organization: Any) -> None:
    organization_id = _organization_id(organization)
    if not organization_id:
        return

    key = _org_version_key(organization_id)
    try:
        cache.incr(key)
    except ValueError:
        cache.set(key, 2, timeout=ORG_CACHE_VERSION_TIMEOUT)


def org_cache_key(namespace: str, organization: Any, *parts: object) -> str:
    organization_id = _organization_id(organization)
    version = get_org_cache_version(organization_id)
    raw = ":".join(str(part) for part in parts if part is not None)
    digest = sha256(raw.encode()).hexdigest()[:24] if raw else "root"
    return f"{namespace}:org:{organization_id}:v{version}:{digest}"


def _organization_id(organization: Any) -> str:
    return str(getattr(organization, "id", organization) or "")


def _org_version_key(organization_id: str) -> str:
    return f"org-cache-version:{organization_id}"
