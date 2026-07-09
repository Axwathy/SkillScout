"""
Candidate-specific auth views.
POST /api/v1/candidate/auth/register/
Candidates self-register with no org and no approval step.
"""

from django.conf import settings
from rest_framework import status, views
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.serializers import CandidateRegisterSerializer, UserSerializer


class CandidateRegisterView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = CandidateRegisterSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Issue JWT cookies immediately — no approval step for candidates
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        response = Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

        is_secure = not settings.DEBUG
        cookie_kwargs = dict(
            httponly=True,
            samesite="Lax",
            secure=is_secure,
            path="/",
        )
        response.set_cookie("access", access_token, max_age=60 * 15, **cookie_kwargs)
        response.set_cookie("refresh", refresh_token, max_age=60 * 60 * 24 * 7, **cookie_kwargs)
        return response
