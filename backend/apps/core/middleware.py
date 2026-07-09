from __future__ import annotations

import logging

from django.conf import settings

logger = logging.getLogger("security.audit")


class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response.setdefault("X-Content-Type-Options", "nosniff")
        response.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")

        csp = getattr(settings, "CONTENT_SECURITY_POLICY", "")
        if csp:
            response.setdefault("Content-Security-Policy", csp)

        return response


class ApiSecurityAuditMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.path.startswith("/api/") and request.method in {"POST", "PATCH", "DELETE"}:
            user = getattr(request, "user", None)
            logger.info(
                "api_request method=%s path=%s status=%s user=%s ip=%s",
                request.method,
                request.path,
                response.status_code,
                getattr(user, "id", None) if getattr(user, "is_authenticated", False) else None,
                request.META.get("REMOTE_ADDR", ""),
            )
        return response
