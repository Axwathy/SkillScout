from celery import shared_task
from django.utils.dateparse import parse_date

from apps.analytics.services import create_daily_snapshot
from apps.organizations.models import Organization


@shared_task
def precompute_daily_analytics_snapshots(snapshot_date: str | None = None) -> int:
    parsed_date = parse_date(snapshot_date) if snapshot_date else None
    count = 0
    for organization in Organization.objects.all().only("id"):
        create_daily_snapshot(organization, snapshot_date=parsed_date)
        count += 1
    return count
