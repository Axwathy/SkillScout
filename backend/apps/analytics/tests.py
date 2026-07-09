from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import Recruiter, User
from apps.analytics import services
from apps.analytics.models import DailyAnalyticsSnapshot
from apps.candidates.models import Application, Candidate
from apps.jobs.models import Job
from apps.organizations.models import Organization

pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    return APIClient()


def make_recruiter(email="recruiter@example.com", organization=None):
    user = User.objects.create_user(
        email=email,
        password="StrongPass123!",
        role=User.Role.RECRUITER,
        first_name="Rina",
        last_name="Shah",
    )
    organization = organization or Organization.objects.create(
        name=f"{email} Org",
        approval_status=Organization.ApprovalStatus.APPROVED,
    )
    Recruiter.objects.create(
        user=user,
        first_name="Rina",
        last_name="Shah",
        organization=organization,
        verification_status=Recruiter.VerificationStatus.APPROVED,
        is_verified=True,
    )
    return user, organization


def make_job(organization, user, status=Job.Status.PUBLISHED):
    return Job.objects.create(
        organization=organization,
        created_by=user,
        title="Backend Engineer",
        description="Build APIs.",
        requirements="Python.",
        location="Remote",
        employment_type=Job.EmploymentType.FULL_TIME,
        status=status,
    )


def make_application(
    organization,
    job,
    email,
    *,
    statuses=(),
    source=Application.Source.DIRECT,
    user=None,
):
    candidate = Candidate.objects.create(
        organization=organization,
        first_name=email.split("@", 1)[0].title(),
        last_name="Candidate",
        email=email,
    )
    application = Application.objects.create(
        candidate=candidate,
        job=job,
        organization=organization,
        source=source,
    )
    for status in statuses:
        application.transition_status(status, changed_by=user)
    return application


def test_funnel_counts_and_conversion():
    user, org = make_recruiter()
    job = make_job(org, user)
    make_application(org, job, "a@example.com", statuses=["under_review"])
    make_application(org, job, "b@example.com", statuses=["technical_round", "rejected"])
    make_application(org, job, "c@example.com", statuses=["hired"])

    funnel = services.compute_funnel(org)
    counts = {stage["stage"]: stage["count"] for stage in funnel["stages"]}

    assert funnel["total"] == 3
    assert counts["applications"] == 3
    assert counts["screened"] == 3  # all moved out of applied
    assert counts["interviewed"] == 2  # technical (then rejected) + hired
    assert counts["offers"] == 1  # the hired one passed the offer threshold
    assert counts["hires"] == 1

    screened_stage = next(s for s in funnel["stages"] if s["stage"] == "screened")
    assert screened_stage["conversion_from_prior"] == 1.0  # 3/3


def test_time_to_hire_average_and_median():
    user, org = make_recruiter()
    job = make_job(org, user)
    app = make_application(org, job, "hire@example.com", statuses=["hired"])
    # Backdate the application so the hire took ~5 days (update bypasses auto_now_add).
    Application.objects.filter(id=app.id).update(applied_at=timezone.now() - timedelta(days=5))

    result = services.compute_time_to_hire(org)
    assert result["overall"]["count"] == 1
    assert 4.5 <= result["overall"]["average_days"] <= 5.5
    assert result["overall"]["median_days"] is not None
    assert result["by_job"][0]["job_title"] == "Backend Engineer"


def test_overview_kpis():
    user, org = make_recruiter()
    job = make_job(org, user)
    make_application(org, job, "p@example.com", statuses=["under_review"])
    make_application(org, job, "q@example.com", statuses=["hired"])

    overview = services.compute_overview(org)
    assert overview["total_applications"] == 2
    assert overview["open_positions"] == 1
    assert overview["in_pipeline"] == 1  # under_review (hired is terminal)
    assert overview["hires"] == 1
    assert overview["offer_acceptance_rate"] == 1.0  # 1 hire / 1 reached offer


def test_date_range_filter_excludes_older_applications():
    user, org = make_recruiter()
    job = make_job(org, user)
    old = make_application(org, job, "old@example.com")
    Application.objects.filter(id=old.id).update(applied_at=timezone.now() - timedelta(days=60))
    make_application(org, job, "new@example.com")

    start, end = services.parse_date_range(
        {"start": (timezone.now() - timedelta(days=7)).date().isoformat()}
    )
    funnel = services.compute_funnel(org, start=start, end=end)
    assert funnel["total"] == 1


def test_org_isolation():
    user_a, org_a = make_recruiter("a@example.com")
    _, org_b = make_recruiter("b@example.com")
    job_a = make_job(org_a, user_a)
    make_application(org_a, job_a, "x@example.com")

    assert services.compute_overview(org_b)["total_applications"] == 0


def test_overview_endpoint_requires_recruiter_and_returns_kpis(api_client):
    user, org = make_recruiter()
    job = make_job(org, user)
    make_application(org, job, "z@example.com", statuses=["under_review"])
    api_client.force_authenticate(user=user)

    response = api_client.get(reverse("analytics-overview"))
    assert response.status_code == 200
    assert response.json()["total_applications"] == 1
    assert response.json()["open_positions"] == 1


def test_source_effectiveness_counts_hires_by_source():
    user, org = make_recruiter()
    job = make_job(org, user)
    make_application(
        org,
        job,
        "linkedin@example.com",
        statuses=["hired"],
        source=Application.Source.LINKEDIN,
    )
    make_application(org, job, "direct@example.com", source=Application.Source.DIRECT)

    result = services.compute_source_effectiveness(org)
    sources = {row["source"]: row for row in result["sources"]}

    assert sources[Application.Source.LINKEDIN]["applications"] == 1
    assert sources[Application.Source.LINKEDIN]["hires"] == 1
    assert sources[Application.Source.LINKEDIN]["conversion_rate"] == 1.0
    assert sources[Application.Source.DIRECT]["applications"] == 1


def test_team_activity_counts_recruiter_work():
    user, org = make_recruiter()
    job = make_job(org, user)
    make_application(
        org,
        job,
        "screened@example.com",
        statuses=["under_review", "technical_round", "hired"],
        user=user,
    )

    result = services.compute_team_activity(org)

    assert result["recruiters"][0]["email"] == user.email
    assert result["recruiters"][0]["status_updates"] == 3
    assert result["recruiters"][0]["candidates_processed"] == 1
    assert result["recruiters"][0]["interviews_conducted"] == 1
    assert result["recruiters"][0]["hires"] == 1


def test_dashboard_endpoint_returns_14b_sections(api_client):
    user, org = make_recruiter()
    job = make_job(org, user)
    make_application(org, job, "dash@example.com", statuses=["under_review"], user=user)
    api_client.force_authenticate(user=user)

    response = api_client.get(reverse("analytics-dashboard"))

    assert response.status_code == 200
    payload = response.json()
    assert set(payload) == {"overview", "funnel", "time_to_hire", "sources", "team_activity"}
    assert "trends" in payload["overview"]
    assert "series" in payload["overview"]


def test_export_sources_csv(api_client):
    user, org = make_recruiter()
    job = make_job(org, user)
    make_application(org, job, "csv@example.com", source=Application.Source.REFERRAL)
    api_client.force_authenticate(user=user)

    response = api_client.get(reverse("analytics-export"), {"metric": "sources"})

    assert response.status_code == 200
    assert response["Content-Type"] == "text/csv"
    assert "source_label,applications,offers,hires" in response.content.decode()
    assert "Referral" in response.content.decode()


def test_create_daily_snapshot():
    user, org = make_recruiter()
    job = make_job(org, user)
    make_application(org, job, "snapshot@example.com", statuses=["hired"])

    snapshot = services.create_daily_snapshot(org)

    assert DailyAnalyticsSnapshot.objects.count() == 1
    assert snapshot.overview["hires"] == 1
    assert snapshot.funnel["total"] == 1
