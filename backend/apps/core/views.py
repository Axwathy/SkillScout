from django.db import OperationalError, connection
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthCheckView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        database_status = "ok"
        response_status = status.HTTP_200_OK

        try:
            connection.ensure_connection()
        except OperationalError:
            database_status = "unavailable"
            response_status = status.HTTP_503_SERVICE_UNAVAILABLE

        return Response(
            {
                "service": "ai-recruitment-api",
                "status": "ok" if database_status == "ok" else "degraded",
                "database": database_status,
            },
            status=response_status,
        )

