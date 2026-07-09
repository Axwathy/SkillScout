import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMessage

logger = logging.getLogger(__name__)


@shared_task(
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_jitter=True,
    retry_kwargs={"max_retries": 2},
)
def send_notification_email(recipient_email, title, body, event_type="", data=None):
    """Send a single plain-text notification email.

    Uses Django's configured email backend (console in dev, SMTP in prod), so no
    provider SDK is required. Runs inline in dev where Celery is eager.
    """
    if not recipient_email:
        return

    lines = [body or title]
    url = (data or {}).get("url")
    if url:
        base = getattr(settings, "FRONTEND_BASE_URL", "").rstrip("/")
        lines.extend(["", f"Open: {base}{url}" if base else f"Open: {url}"])

    EmailMessage(
        subject=title,
        body="\n".join(lines),
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
        to=[recipient_email],
    ).send(fail_silently=False)
    logger.info("Sent notification email to %s (%s)", recipient_email, event_type)
