import logging

from django.conf import settings
from django.utils import timezone

from .models import Notification, NotificationPreference

logger = logging.getLogger(__name__)


def _preference(user, event_type) -> NotificationPreference | None:
    return NotificationPreference.objects.filter(user=user, event_type=event_type).first()


def notify(
    recipient,
    event_type,
    *,
    title,
    body="",
    data=None,
    organization=None,
    actor=None,
):
    """Create an in-app notification and/or send an email, honoring preferences.

    No-ops when the recipient is the actor (you don't notify yourself about your
    own action). Returns the created Notification, or None when the in-app
    channel is disabled (an email may still be sent).
    """
    if recipient is None:
        return None
    if actor is not None and getattr(actor, "id", None) == getattr(recipient, "id", None):
        return None

    preference = _preference(recipient, event_type)
    in_app_enabled = preference.in_app_enabled if preference else True
    email_enabled = preference.email_enabled if preference else True

    notification = None
    if in_app_enabled:
        notification = Notification.objects.create(
            recipient=recipient,
            organization=organization,
            event_type=event_type,
            title=title,
            body=body,
            data=data or {},
        )

    if email_enabled and getattr(recipient, "email", ""):
        _enqueue_email(recipient.email, event_type, title, body, data or {})

    return notification


def _enqueue_email(recipient_email, event_type, title, body, data):
    from .tasks import send_notification_email

    # Mirror dispatch_resume_parse: run inline when Celery is eager (dev/tests),
    # otherwise queue to the worker and fall back to inline if the broker is down.
    if getattr(settings, "CELERY_TASK_ALWAYS_EAGER", False):
        send_notification_email(recipient_email, title, body, event_type, data)
        return
    try:
        send_notification_email.delay(recipient_email, title, body, event_type, data)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Failed to enqueue notification email to %s: %s", recipient_email, exc)
        send_notification_email(recipient_email, title, body, event_type, data)


def notify_recruiters_for_job(job, event_type, *, title, body="", data=None, actor=None):
    """Notify the job owner about a job-related event.

    Scoped to ``job.created_by`` for now; can fan out to all org recruiters
    (``job.organization.recruiters``) when team assignment lands.
    """
    return notify(
        getattr(job, "created_by", None),
        event_type,
        title=title,
        body=body,
        data=data,
        organization=job.organization,
        actor=actor,
    )


def mark_all_read(user) -> int:
    return Notification.objects.filter(recipient=user, read_at__isnull=True).update(
        read_at=timezone.now()
    )
