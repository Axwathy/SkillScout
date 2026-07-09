"""Recruitment analytics aggregation.

Dashboard metrics are derived from application data and cached briefly. Daily
snapshots are available for pre-computation/reporting, but live endpoints still
compute from source records so recent changes show up without waiting for a job.
"""

import csv
import io
import statistics
from datetime import datetime, time, timedelta

from django.core.cache import cache
from django.db.models import Count, Q
from django.utils.dateparse import parse_date
from django.utils.timezone import localdate, make_aware

from apps.analytics.models import DailyAnalyticsSnapshot
from apps.candidates.models import Application, ApplicationHistory
from apps.core.cache import get_org_cache_version
from apps.jobs.models import Job

STATUS_RANK = {
    Application.Status.APPLIED: 1,
    Application.Status.UNDER_REVIEW: 2,
    Application.Status.SHORTLISTED: 3,
    Application.Status.TECHNICAL_ROUND: 4,
    Application.Status.HR_ROUND: 5,
    Application.Status.OFFER: 6,
    Application.Status.HIRED: 7,
}

FUNNEL_BUCKETS = [
    ("applications", 1),
    ("screened", 2),
    ("interviewed", 4),
    ("offers", 6),
    ("hires", 7),
]

TERMINAL_STATUSES = {Application.Status.HIRED, Application.Status.REJECTED}
INTERVIEW_STATUSES = {Application.Status.TECHNICAL_ROUND, Application.Status.HR_ROUND}
ANALYTICS_CACHE_SECONDS = 60

SOURCE_LABELS = {
    Application.Source.DIRECT: "Direct",
    Application.Source.JOB_BOARD: "Job Board",
    Application.Source.LINKEDIN: "LinkedIn",
    Application.Source.REFERRAL: "Referral",
    Application.Source.AGENCY: "Agency",
    Application.Source.OTHER: "Other",
}


def _to_datetime(value, *, end):
    parsed = parse_date(value) if value else None
    if not parsed:
        return None
    return make_aware(datetime.combine(parsed, time.max if end else time.min))


def parse_date_range(params):
    """Return (start, end) aware datetimes from ?start=YYYY-MM-DD&end=YYYY-MM-DD."""
    return _to_datetime(params.get("start"), end=False), _to_datetime(params.get("end"), end=True)


def analytics_cache_key(metric: str, organization, *, start=None, end=None, extra=""):
    start_value = start.isoformat() if start else ""
    end_value = end.isoformat() if end else ""
    version = get_org_cache_version(organization)
    return f"analytics:{metric}:{organization.id}:v{version}:{start_value}:{end_value}:{extra}"


def cached_metric(metric: str, organization, calculator, *, start=None, end=None, extra=""):
    key = analytics_cache_key(metric, organization, start=start, end=end, extra=extra)
    value = cache.get(key)
    if value is not None:
        return value
    value = calculator()
    cache.set(key, value, ANALYTICS_CACHE_SECONDS)
    return value


def _base_applications(organization, start=None, end=None):
    queryset = Application.objects.filter(organization=organization)
    if start:
        queryset = queryset.filter(applied_at__gte=start)
    if end:
        queryset = queryset.filter(applied_at__lte=end)
    return queryset


def _history_by_application(application_ids):
    grouped: dict = {}
    for row in ApplicationHistory.objects.filter(application_id__in=application_ids).only(
        "application_id", "to_status"
    ):
        grouped.setdefault(row.application_id, []).append(row.to_status)
    return grouped


def _max_rank_reached(status, history_statuses):
    ranks = [STATUS_RANK.get(status, 0)]
    ranks.extend(STATUS_RANK.get(value, 0) for value in history_statuses)
    return max(ranks)


def compute_funnel(organization, *, job=None, start=None, end=None):
    queryset = _base_applications(organization, start, end)
    if job is not None:
        queryset = queryset.filter(job=job)
    applications = list(queryset.only("id", "status"))
    history = _history_by_application([application.id for application in applications])

    counts = {label: 0 for label, _ in FUNNEL_BUCKETS}
    for application in applications:
        rank = _max_rank_reached(application.status, history.get(application.id, []))
        for label, threshold in FUNNEL_BUCKETS:
            if rank >= threshold:
                counts[label] += 1

    stages = []
    prior = None
    for label, _ in FUNNEL_BUCKETS:
        count = counts[label]
        stages.append(
            {
                "stage": label,
                "count": count,
                "conversion_from_prior": round(count / prior, 4) if prior else None,
            }
        )
        prior = count

    return {"total": counts["applications"], "stages": stages}


def compute_time_to_hire(organization, *, start=None, end=None):
    applications = list(
        _base_applications(organization, start, end)
        .select_related("job")
        .only("id", "applied_at", "job__id", "job__title")
    )
    hired_at = _latest_hired_transition([application.id for application in applications])

    durations: list[float] = []
    by_job: dict = {}
    for application in applications:
        hired_time = hired_at.get(application.id)
        if not hired_time:
            continue
        days = (hired_time - application.applied_at).total_seconds() / 86400
        if days < 0:
            continue
        durations.append(days)
        bucket = by_job.setdefault(
            application.job_id,
            {"job_title": application.job.title, "days": []},
        )
        bucket["days"].append(days)

    return {
        "overall": _duration_summary(durations),
        "by_job": sorted(
            (
                {
                    "job_id": str(job_id),
                    "job_title": data["job_title"],
                    **_duration_summary(data["days"]),
                }
                for job_id, data in by_job.items()
            ),
            key=lambda item: item["average_days"] or 0,
            reverse=True,
        ),
    }


def _latest_hired_transition(application_ids):
    hired_at: dict = {}
    for row in (
        ApplicationHistory.objects.filter(
            application_id__in=application_ids,
            to_status=Application.Status.HIRED,
        )
        .order_by("application_id", "-changed_at")
        .only("application_id", "changed_at")
    ):
        hired_at.setdefault(row.application_id, row.changed_at)
    return hired_at


def _duration_summary(days: list[float]):
    if not days:
        return {"count": 0, "average_days": None, "median_days": None}
    return {
        "count": len(days),
        "average_days": round(statistics.mean(days), 1),
        "median_days": round(statistics.median(days), 1),
    }


def compute_overview(organization, *, start=None, end=None, include_trends=True):
    applications = _base_applications(organization, start, end)
    funnel = compute_funnel(organization, start=start, end=end)
    stage_counts = {stage["stage"]: stage["count"] for stage in funnel["stages"]}
    hires = stage_counts.get("hires", 0)
    offers_reached = stage_counts.get("offers", 0)
    time_to_hire = compute_time_to_hire(organization, start=start, end=end)["overall"]

    current = {
        "total_applications": stage_counts.get("applications", 0),
        "open_positions": Job.objects.filter(
            organization=organization,
            status=Job.Status.PUBLISHED,
        ).count(),
        "in_pipeline": applications.exclude(status__in=TERMINAL_STATUSES).count(),
        "hires": hires,
        "average_time_to_hire_days": time_to_hire["average_days"],
        "offer_acceptance_rate": round(hires / offers_reached, 4) if offers_reached else None,
    }
    current["trends"] = (
        _overview_trends(organization, current, start=start, end=end)
        if include_trends
        else {key: None for key in _trend_metrics()}
    )
    current["series"] = (
        _overview_series(organization, start=start, end=end) if include_trends else []
    )
    return current


def compute_source_effectiveness(organization, *, start=None, end=None):
    applications = list(_base_applications(organization, start, end).only("id", "source", "status"))
    history = _history_by_application([application.id for application in applications])
    buckets = {
        source: {
            "source": source,
            "source_label": label,
            "applications": 0,
            "offers": 0,
            "hires": 0,
            "conversion_rate": None,
            "cost_per_hire": None,
        }
        for source, label in SOURCE_LABELS.items()
    }

    for application in applications:
        bucket = buckets.setdefault(
            application.source,
            {
                "source": application.source,
                "source_label": application.source.replace("_", " ").title(),
                "applications": 0,
                "offers": 0,
                "hires": 0,
                "conversion_rate": None,
                "cost_per_hire": None,
            },
        )
        bucket["applications"] += 1
        rank = _max_rank_reached(application.status, history.get(application.id, []))
        if rank >= STATUS_RANK[Application.Status.OFFER]:
            bucket["offers"] += 1
        if rank >= STATUS_RANK[Application.Status.HIRED]:
            bucket["hires"] += 1

    rows = []
    for bucket in buckets.values():
        count = bucket["applications"]
        bucket["conversion_rate"] = round(bucket["hires"] / count, 4) if count else None
        rows.append(bucket)

    return {
        "sources": sorted(
            rows,
            key=lambda item: (item["applications"], item["hires"], item["source_label"]),
            reverse=True,
        )
    }


def compute_team_activity(organization, *, start=None, end=None):
    history = ApplicationHistory.objects.filter(application__organization=organization)
    if start:
        history = history.filter(changed_at__gte=start)
    if end:
        history = history.filter(changed_at__lte=end)

    rows = (
        history.filter(changed_by__isnull=False)
        .values(
            "changed_by_id",
            "changed_by__email",
            "changed_by__first_name",
            "changed_by__last_name",
        )
        .annotate(
            status_updates=Count("id"),
            candidates_processed=Count("application_id", distinct=True),
            interviews_conducted=Count("id", filter=Q(to_status__in=INTERVIEW_STATUSES)),
            hires=Count("id", filter=Q(to_status=Application.Status.HIRED)),
        )
        .order_by("-candidates_processed", "-status_updates", "changed_by__email")
    )

    first_response = _first_response_hours(organization, start=start, end=end)
    recruiters = []
    for row in rows:
        recruiter_id = row["changed_by_id"]
        first_name = row["changed_by__first_name"] or ""
        last_name = row["changed_by__last_name"] or ""
        name = f"{first_name} {last_name}".strip() or row["changed_by__email"]
        recruiters.append(
            {
                "recruiter_id": str(recruiter_id),
                "name": name,
                "email": row["changed_by__email"],
                "status_updates": row["status_updates"],
                "candidates_processed": row["candidates_processed"],
                "interviews_conducted": row["interviews_conducted"],
                "hires": row["hires"],
                "average_response_hours": first_response.get(recruiter_id),
            }
        )

    return {"recruiters": recruiters}


def compute_dashboard(organization, *, start=None, end=None):
    return {
        "overview": cached_metric(
            "overview",
            organization,
            lambda: compute_overview(organization, start=start, end=end),
            start=start,
            end=end,
        ),
        "funnel": cached_metric(
            "funnel",
            organization,
            lambda: compute_funnel(organization, start=start, end=end),
            start=start,
            end=end,
        ),
        "time_to_hire": cached_metric(
            "time-to-hire",
            organization,
            lambda: compute_time_to_hire(organization, start=start, end=end),
            start=start,
            end=end,
        ),
        "sources": cached_metric(
            "sources",
            organization,
            lambda: compute_source_effectiveness(organization, start=start, end=end),
            start=start,
            end=end,
        ),
        "team_activity": cached_metric(
            "team-activity",
            organization,
            lambda: compute_team_activity(organization, start=start, end=end),
            start=start,
            end=end,
        ),
    }


def create_daily_snapshot(organization, snapshot_date=None):
    snapshot_date = snapshot_date or localdate()
    start = make_aware(datetime.combine(snapshot_date, time.min))
    end = make_aware(datetime.combine(snapshot_date, time.max))
    payload = compute_dashboard(organization, start=start, end=end)
    snapshot, _created = DailyAnalyticsSnapshot.objects.update_or_create(
        organization=organization,
        snapshot_date=snapshot_date,
        defaults={
            "overview": payload["overview"],
            "funnel": payload["funnel"],
            "time_to_hire": payload["time_to_hire"],
            "sources": payload["sources"],
            "team_activity": payload["team_activity"],
        },
    )
    return snapshot


def export_csv(metric: str, organization, *, start=None, end=None) -> str:
    metric = metric or "overview"
    if metric == "overview":
        rows = _overview_csv_rows(compute_overview(organization, start=start, end=end))
        headers = ["metric", "value"]
    elif metric == "funnel":
        rows = compute_funnel(organization, start=start, end=end)["stages"]
        headers = ["stage", "count", "conversion_from_prior"]
    elif metric == "time-to-hire":
        rows = compute_time_to_hire(organization, start=start, end=end)["by_job"]
        headers = ["job_id", "job_title", "count", "average_days", "median_days"]
    elif metric == "sources":
        rows = compute_source_effectiveness(organization, start=start, end=end)["sources"]
        headers = [
            "source",
            "source_label",
            "applications",
            "offers",
            "hires",
            "conversion_rate",
            "cost_per_hire",
        ]
    elif metric == "team-activity":
        rows = compute_team_activity(organization, start=start, end=end)["recruiters"]
        headers = [
            "recruiter_id",
            "name",
            "email",
            "status_updates",
            "candidates_processed",
            "interviews_conducted",
            "hires",
            "average_response_hours",
        ]
    else:
        raise ValueError("Unsupported analytics export metric.")

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=headers, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


def _overview_trends(organization, current, *, start=None, end=None):
    if not start:
        return {key: None for key in _trend_metrics()}

    current_end = end or make_aware(datetime.combine(localdate(), time.max))
    period = current_end - start
    if period.total_seconds() <= 0:
        return {key: None for key in _trend_metrics()}

    previous_end = start - timedelta(microseconds=1)
    previous_start = previous_end - period
    previous = compute_overview(
        organization,
        start=previous_start,
        end=previous_end,
        include_trends=False,
    )
    return {
        metric: _delta_percent(current.get(metric), previous.get(metric))
        for metric in _trend_metrics()
    }


def _overview_series(organization, *, start=None, end=None):
    if not start:
        start = make_aware(datetime.combine(localdate() - timedelta(days=29), time.min))
    if not end:
        end = make_aware(datetime.combine(localdate(), time.max))

    application_rows = (
        _base_applications(organization, start, end)
        .values("applied_at__date")
        .annotate(count=Count("id"))
    )
    applications_by_date = {
        row["applied_at__date"]: row["count"]
        for row in application_rows
        if row["applied_at__date"] is not None
    }
    hired_rows = (
        ApplicationHistory.objects.filter(
            application__organization=organization,
            to_status=Application.Status.HIRED,
            changed_at__gte=start,
            changed_at__lte=end,
        )
        .values("changed_at__date")
        .annotate(count=Count("id"))
    )
    hires_by_date = {
        row["changed_at__date"]: row["count"]
        for row in hired_rows
        if row["changed_at__date"] is not None
    }

    days = []
    cursor = start.date()
    while cursor <= end.date():
        days.append(
            {
                "date": cursor.isoformat(),
                "applications": applications_by_date.get(cursor, 0),
                "hires": hires_by_date.get(cursor, 0),
            }
        )
        cursor += timedelta(days=1)
    return days


def _first_response_hours(organization, *, start=None, end=None):
    applications = _base_applications(organization, start, end).only("id", "applied_at")
    application_applied_at = {
        application.id: application.applied_at
        for application in applications
    }
    history = (
        ApplicationHistory.objects.filter(
            application_id__in=application_applied_at.keys(),
            changed_by__isnull=False,
        )
        .order_by("application_id", "changed_at")
        .only("application_id", "changed_by_id", "changed_at")
    )
    first_by_recruiter: dict = {}
    seen_applications = set()
    for row in history:
        if row.application_id in seen_applications:
            continue
        seen_applications.add(row.application_id)
        applied_at = application_applied_at.get(row.application_id)
        if not applied_at:
            continue
        hours = (row.changed_at - applied_at).total_seconds() / 3600
        if hours >= 0:
            first_by_recruiter.setdefault(row.changed_by_id, []).append(hours)

    return {
        recruiter_id: round(statistics.mean(hours), 1)
        for recruiter_id, hours in first_by_recruiter.items()
        if hours
    }


def _overview_csv_rows(overview):
    return [
        {"metric": "total_applications", "value": overview["total_applications"]},
        {"metric": "open_positions", "value": overview["open_positions"]},
        {"metric": "in_pipeline", "value": overview["in_pipeline"]},
        {"metric": "hires", "value": overview["hires"]},
        {
            "metric": "average_time_to_hire_days",
            "value": overview["average_time_to_hire_days"],
        },
        {"metric": "offer_acceptance_rate", "value": overview["offer_acceptance_rate"]},
    ]


def _trend_metrics():
    return [
        "total_applications",
        "open_positions",
        "in_pipeline",
        "hires",
        "average_time_to_hire_days",
        "offer_acceptance_rate",
    ]


def _delta_percent(current, previous):
    if current is None or previous in (None, 0):
        return None
    return round((float(current) - float(previous)) / abs(float(previous)), 4)
