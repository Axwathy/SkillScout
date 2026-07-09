from django.conf import settings
from django.middleware.csrf import CsrfViewMiddleware
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed, InvalidToken, TokenError
from rest_framework_simplejwt.settings import api_settings

from .models import User


class CSRFCheck(CsrfViewMiddleware):
    def _reject(self, request, reason):
        return reason


class CookieJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication that reads the access token from an HttpOnly
    cookie named 'access' instead of the Authorization header.

    Falls back to the Authorization header so DRF browsable API and
    Postman/curl testing with Bearer tokens still works in development.

    See: raw/architecture/cookie-auth-strategy.md
    """

    def authenticate(self, request):
        # 1. Try the HttpOnly cookie first (production path)
        raw_token = request.COOKIES.get("access")
        token_from_cookie = raw_token is not None

        if raw_token is None:
            # 2. Fall back to Authorization header (dev/Postman convenience)
            header = self.get_header(request)
            if header is None:
                return None
            raw_token = self.get_raw_token(header)
            if raw_token is None:
                return None

        try:
            validated_token = self.get_validated_token(raw_token)
        except TokenError as e:
            raise InvalidToken(e.args[0]) from e

        if token_from_cookie and self._should_enforce_csrf(request):
            self._enforce_csrf(request)

        return self.get_user(validated_token), validated_token

    def _should_enforce_csrf(self, request) -> bool:
        if request.method in {"GET", "HEAD", "OPTIONS", "TRACE"}:
            return False
        return bool(getattr(settings, "ENFORCE_CSRF_ON_COOKIE_AUTH", False))

    def _enforce_csrf(self, request) -> None:
        check = CSRFCheck(lambda req: None)
        check.process_request(request)
        reason = check.process_view(request, None, (), {})
        if reason:
            raise PermissionDenied(f"CSRF validation failed: {reason}")

    def get_user(self, validated_token):
        try:
            user_id = validated_token[api_settings.USER_ID_CLAIM]
        except KeyError as exc:
            raise InvalidToken("Token contained no recognizable user identification") from exc

        try:
            user = User.objects.select_related("recruiter_profile__organization").get(
                **{api_settings.USER_ID_FIELD: user_id}
            )
        except User.DoesNotExist as exc:
            raise AuthenticationFailed("User not found", code="user_not_found") from exc

        if not user.is_active:
            raise AuthenticationFailed("User is inactive", code="user_inactive")

        return user
