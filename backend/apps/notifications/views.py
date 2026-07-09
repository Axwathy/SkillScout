from rest_framework import generics, views
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Notification, NotificationPreference
from .serializers import NotificationSerializer
from .services import mark_all_read


def _truthy(value) -> bool:
    return str(value or "").lower() in {"1", "true", "yes"}


class NotificationListView(generics.ListAPIView):
    """GET /api/v1/notifications/  (?unread=true to filter)"""

    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Notification.objects.filter(recipient=self.request.user)
        if _truthy(self.request.query_params.get("unread")):
            queryset = queryset.filter(read_at__isnull=True)
        # Newest-first (model Meta ordering); cap the dropdown payload.
        return queryset[:100]


class UnreadCountView(views.APIView):
    """GET /api/v1/notifications/unread-count/ — cheap badge poll."""

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        count = Notification.objects.filter(
            recipient=request.user,
            read_at__isnull=True,
        ).count()
        return Response({"unread": count})


class NotificationReadView(views.APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk, *args, **kwargs):
        notification = generics.get_object_or_404(Notification, pk=pk, recipient=request.user)
        notification.mark_read()
        return Response(NotificationSerializer(notification).data)


class MarkAllReadView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        return Response({"marked_read": mark_all_read(request.user)})


class NotificationPreferenceView(views.APIView):
    """GET/PATCH /api/v1/notifications/preferences/ — full event x channel matrix."""

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return Response(self._matrix(request.user))

    def patch(self, request, *args, **kwargs):
        payload = request.data
        items = payload if isinstance(payload, list) else payload.get("preferences", [])
        for item in items:
            event_type = item.get("event_type")
            if event_type not in Notification.EventType.values:
                continue
            defaults = {}
            if "email_enabled" in item:
                defaults["email_enabled"] = bool(item["email_enabled"])
            if "in_app_enabled" in item:
                defaults["in_app_enabled"] = bool(item["in_app_enabled"])
            if not defaults:
                continue
            NotificationPreference.objects.update_or_create(
                user=request.user,
                event_type=event_type,
                defaults=defaults,
            )
        return Response(self._matrix(request.user))

    def _matrix(self, user):
        existing = {
            preference.event_type: preference
            for preference in NotificationPreference.objects.filter(user=user)
        }
        rows = [
            {
                "event_type": value,
                "label": label,
                "email_enabled": existing[value].email_enabled if value in existing else True,
                "in_app_enabled": existing[value].in_app_enabled if value in existing else True,
            }
            for value, label in Notification.EventType.choices
        ]
        return {"preferences": rows}
