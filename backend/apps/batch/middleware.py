from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken

from apps.accounts.models import User


class CookieJWTAuthMiddleware:
    """Authenticate WebSocket connections with the existing access cookie."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        token = _token_from_scope(scope)
        scope["user"] = await self._get_user(token) if token else AnonymousUser()
        return await self.app(scope, receive, send)

    @database_sync_to_async
    def _get_user(self, token):
        try:
            validated = AccessToken(token)
            user_id = validated.get("user_id")
            return User.objects.get(id=user_id, is_active=True)
        except (TokenError, User.DoesNotExist, TypeError, ValueError):
            return AnonymousUser()


def _token_from_scope(scope) -> str | None:
    headers = dict(scope.get("headers") or [])
    cookie_header = headers.get(b"cookie", b"").decode("latin1")
    for part in cookie_header.split(";"):
        if "=" not in part:
            continue
        key, value = part.strip().split("=", 1)
        if key == "access" and value:
            return value

    query_string = scope.get("query_string", b"").decode("latin1")
    query = parse_qs(query_string)
    token_values = query.get("token") or []
    return token_values[0] if token_values else None
