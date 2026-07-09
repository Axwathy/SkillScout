from datetime import timedelta
from unittest.mock import patch

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import Recruiter, User
from apps.batch.models import BatchItem, BatchJob, ScheduledBatchOperation
from apps.candidates.models import Application, Candidate
from apps.candidates.resume_parser import ParseResult
from apps.jobs.models import Job
from apps.organizations.models import Organization

pytestmark = pytest.mark.django_db


@pytest.fixture(autouse=True)
def in_memory_channel_layer(settings):
    settings.CHANNEL_LAYERS = {
        "default": {"BACKEND": "channels.layers.InMemoryChannelLayer"},
    }
    settings.BATCH_TASK_RUN_INLINE = True


@pytest.fixture
def api_client():
    return APIClient()


def create_recruiter(email="recruiter@example.com"):
    user = User.objects.create_user(
        email=email,
        password="StrongPass123!",
        first_name="Rina",
        last_name="Shah",
        role=User.Role.RECRUITER,
    )
    organization = Organization.objects.create(
        name=f"{email} Org",
        approval_status=Organization.ApprovalStatus.APPROVED,
    )
    Recruiter.objects.create(
        user=user,
        first_name=user.first_name,
        last_name=user.last_name,
        organization=organization,
        verification_status=Recruiter.VerificationStatus.APPROVED,
        is_verified=True,
    )
    return user, organization


def create_job(organization, user, title="Backend Engineer"):
    return Job.objects.create(
        organization=organization,
        created_by=user,
        title=title,
        description="Build hiring workflows.",
        requirements="Python, Django, PostgreSQL. 3 years experience.",
        location="Remote",
        employment_type=Job.EmploymentType.FULL_TIME,
        salary_range="$100k-$130k",
        status=Job.Status.PUBLISHED,
    )


def create_application(organization, job, email="asha@example.com"):
    candidate = Candidate.objects.create(
        organization=organization,
        first_name="Asha",
        last_name="Patel",
        email=email,
    )
    return Application.objects.create(
        candidate=candidate,
        job=job,
        organization=organization,
    )


def parse_result(email="asha@example.com", name="Asha Patel"):
    return ParseResult(
        data={
            "personal_info": {
                "full_name": name,
                "email": email,
                "phone": "5550101",
            },
            "skills": [{"name": "Python"}, {"name": "Django"}],
            "_metadata": {"parsing_confidence": "high"},
        },
        confidence="high",
        model="test-parser",
    )


def resume_file(name="resume.pdf"):
    return SimpleUploadedFile(name, b"%PDF-1.4 resume bytes", content_type="application/pdf")


def test_batch_score_lifecycle_and_progress_endpoint(api_client):
    user, organization = create_recruiter()
    job = create_job(organization, user)
    first = create_application(organization, job, "first@example.com")
    second = create_application(organization, job, "second@example.com")
    api_client.force_authenticate(user=user)

    with patch("apps.batch.services.score_application") as score:
        response = api_client.post(reverse("batch-score", args=[job.id]), format="json")

    assert response.status_code == 201
    batch = BatchJob.objects.get(id=response.json()["id"])
    assert batch.status == BatchJob.Status.COMPLETED
    assert batch.total_count == 2
    assert batch.processed_count == 2
    assert batch.failed_count == 0
    assert set(batch.items.values_list("application_id", flat=True)) == {first.id, second.id}
    assert score.call_count == 2

    progress = api_client.get(reverse("batch-progress", args=[batch.id]), format="json")
    assert progress.status_code == 200
    assert progress.json()["processed_count"] == 2
    assert len(progress.json()["items"]) == 2


def test_bulk_pipeline_action_rejects_selected_applications(api_client):
    user, organization = create_recruiter()
    job = create_job(organization, user)
    first = create_application(organization, job, "first@example.com")
    second = create_application(organization, job, "second@example.com")
    api_client.force_authenticate(user=user)

    response = api_client.post(
        reverse("batch-pipeline-action"),
        {
            "action": "reject",
            "application_ids": [str(first.id), str(second.id)],
        },
        format="json",
    )

    assert response.status_code == 201
    first.refresh_from_db()
    second.refresh_from_db()
    assert first.status == Application.Status.REJECTED
    assert second.status == Application.Status.REJECTED
    assert response.json()["status"] == BatchJob.Status.COMPLETED


def test_bulk_upload_resolves_email_and_placeholder_fallback(api_client):
    user, organization = create_recruiter()
    job = create_job(organization, user)
    api_client.force_authenticate(user=user)

    with (
        patch("apps.batch.services.upload_file"),
        patch("apps.batch.services.extract_text_from_bytes", return_value="resume text"),
        patch(
            "apps.batch.services.parse_resume_text",
            side_effect=[
                parse_result("asha@example.com", "Asha Patel"),
                parse_result("", "No Email"),
            ],
        ),
        patch("apps.batch.services.score_application"),
    ):
        response = api_client.post(
            reverse("batch-upload"),
            {
                "job_id": str(job.id),
                "files": [resume_file("asha.pdf"), resume_file("missing-email.pdf")],
            },
            format="multipart",
        )

    assert response.status_code == 201
    batch = BatchJob.objects.get(id=response.json()["id"])
    assert batch.status == BatchJob.Status.COMPLETED
    assert batch.processed_count == 2
    assert Candidate.objects.filter(organization=organization, email="asha@example.com").exists()
    placeholder = Candidate.objects.get(email__endswith="@placeholder.recruitai.local")
    assert placeholder.first_name == "No"
    assert Application.objects.filter(job=job, candidate=placeholder).exists()
    assert batch.items.filter(metadata__placeholder_email=True).exists()


def test_bulk_upload_records_partial_failure(api_client):
    user, organization = create_recruiter()
    job = create_job(organization, user)
    api_client.force_authenticate(user=user)

    with (
        patch("apps.batch.services.upload_file"),
        patch("apps.batch.services.extract_text_from_bytes", return_value="resume text"),
        patch(
            "apps.batch.services.parse_resume_text",
            side_effect=[parse_result("ok@example.com", "Ok Candidate"), RuntimeError("bad parse")],
        ),
        patch("apps.batch.services.score_application"),
    ):
        response = api_client.post(
            reverse("batch-upload"),
            {
                "job_id": str(job.id),
                "files": [resume_file("ok.pdf"), resume_file("bad.pdf")],
            },
            format="multipart",
        )

    assert response.status_code == 201
    batch = BatchJob.objects.get(id=response.json()["id"])
    assert batch.status == BatchJob.Status.COMPLETED_WITH_ERRORS
    assert batch.processed_count == 2
    assert batch.failed_count == 1
    failed = batch.items.get(status=BatchItem.Status.FAILED)
    assert "bad parse" in failed.error


def test_batch_progress_is_org_scoped(api_client):
    user, organization = create_recruiter("recruiter@example.com")
    other_user, other_org = create_recruiter("other@example.com")
    batch = BatchJob.objects.create(
        organization=other_org,
        initiated_by=other_user,
        job_type=BatchJob.JobType.SCORE,
    )
    api_client.force_authenticate(user=user)

    response = api_client.get(reverse("batch-progress", args=[batch.id]), format="json")

    assert response.status_code == 404
    assert organization != other_org


def test_cancel_batch_sets_cancel_requested(api_client):
    user, organization = create_recruiter()
    batch = BatchJob.objects.create(
        organization=organization,
        initiated_by=user,
        job_type=BatchJob.JobType.SCORE,
        status=BatchJob.Status.RUNNING,
    )
    api_client.force_authenticate(user=user)

    response = api_client.post(reverse("batch-cancel", args=[batch.id]), format="json")

    assert response.status_code == 200
    batch.refresh_from_db()
    assert batch.status == BatchJob.Status.CANCEL_REQUESTED
    assert response.json()["status"] == BatchJob.Status.CANCEL_REQUESTED


def test_active_batch_limit_blocks_new_batch(api_client, settings):
    settings.BATCH_MAX_ACTIVE_PER_ORG = 1
    user, organization = create_recruiter()
    job = create_job(organization, user)
    BatchJob.objects.create(
        organization=organization,
        initiated_by=user,
        job_type=BatchJob.JobType.SCORE,
        status=BatchJob.Status.RUNNING,
    )
    api_client.force_authenticate(user=user)

    response = api_client.post(reverse("batch-score", args=[job.id]), format="json")

    assert response.status_code == 429
    assert "Limit is 1" in response.json()["detail"]


def test_create_and_disable_scheduled_batch(api_client):
    user, organization = create_recruiter()
    job = create_job(organization, user)
    api_client.force_authenticate(user=user)
    run_at = timezone.now() + timedelta(hours=1)

    response = api_client.post(
        reverse("batch-schedule-list"),
        {
            "job_type": BatchJob.JobType.SCORE,
            "params": {"job_id": str(job.id)},
            "frequency": ScheduledBatchOperation.Frequency.DAILY,
            "next_run_at": run_at.isoformat(),
        },
        format="json",
    )

    assert response.status_code == 201
    schedule = ScheduledBatchOperation.objects.get(id=response.json()["id"])
    assert schedule.organization == organization
    assert schedule.frequency == ScheduledBatchOperation.Frequency.DAILY

    delete_response = api_client.delete(reverse("batch-schedule-detail", args=[schedule.id]))
    schedule.refresh_from_db()
    assert delete_response.status_code == 204
    assert schedule.is_active is False
