import pytest
from django.core import mail
from django.urls import reverse
from rest_framework.test import APIClient

from apps.accounts.models import Recruiter, User
from apps.candidates.models import Application, Candidate
from apps.jobs.models import Job
from apps.notifications.models import Notification, NotificationPreference
from apps.notifications.services import notify
from apps.organizations.models import Organization

pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    return APIClient()


def make_recruiter(email, organization=None):
    user = User.objects.create_user(
        email=email,
        password="StrongPass123!",
        role=User.Role.RECRUITER,
        first_name="Rec",
        last_name="Ruiter",
    )
    organization = organization or Organization.objects.create(
        name=f"{email} Org",
        approval_status=Organization.ApprovalStatus.APPROVED,
    )
    Recruiter.objects.create(
        user=user,
        first_name="Rec",
        last_name="Ruiter",
        organization=organization,
        verification_status=Recruiter.VerificationStatus.APPROVED,
        is_verified=True,
    )
    return user, organization


def make_job(organization, owner):
    return Job.objects.create(
        organization=organization,
        created_by=owner,
        title="Backend Engineer",
        description="Build APIs.",
        requirements="Python.",
        location="Remote",
        employment_type=Job.EmploymentType.FULL_TIME,
        status=Job.Status.PUBLISHED,
    )


def make_application(organization, job, email="cand@example.com"):
    candidate = Candidate.objects.create(
        organization=organization,
        first_name="Alice",
        last_name="Smith",
        email=email,
    )
    return Application.objects.create(candidate=candidate, job=job, organization=organization)


def test_notify_creates_in_app_and_email():
    user, org = make_recruiter("rec@example.com")
    notification = notify(
        user,
        Notification.EventType.SYSTEM_ALERT,
        title="Heads up",
        body="Something happened",
        organization=org,
    )
    assert notification is not None
    assert Notification.objects.filter(recipient=user, read_at__isnull=True).count() == 1
    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == [user.email]


def test_notify_skips_self_actor():
    user, _ = make_recruiter("rec@example.com")
    notification = notify(user, Notification.EventType.SYSTEM_ALERT, title="Hi", actor=user)
    assert notification is None
    assert Notification.objects.count() == 0
    assert mail.outbox == []


def test_preferences_disable_both_channels():
    user, _ = make_recruiter("rec@example.com")
    NotificationPreference.objects.create(
        user=user,
        event_type=Notification.EventType.SYSTEM_ALERT,
        email_enabled=False,
        in_app_enabled=False,
    )
    notification = notify(user, Notification.EventType.SYSTEM_ALERT, title="Hi")
    assert notification is None
    assert Notification.objects.count() == 0
    assert mail.outbox == []


def test_preference_email_off_keeps_in_app():
    user, _ = make_recruiter("rec@example.com")
    NotificationPreference.objects.create(
        user=user,
        event_type=Notification.EventType.SYSTEM_ALERT,
        email_enabled=False,
        in_app_enabled=True,
    )
    notification = notify(user, Notification.EventType.SYSTEM_ALERT, title="Hi")
    assert notification is not None
    assert mail.outbox == []


def test_list_unread_count_and_mark_read(api_client):
    user, _ = make_recruiter("rec@example.com")
    notify(user, Notification.EventType.SYSTEM_ALERT, title="One")
    notify(user, Notification.EventType.SYSTEM_ALERT, title="Two")
    api_client.force_authenticate(user=user)

    listed = api_client.get(reverse("notification-list"))
    assert listed.status_code == 200
    assert len(listed.json()) == 2

    assert api_client.get(reverse("notification-unread-count")).json()["unread"] == 2

    first_id = listed.json()[0]["id"]
    assert api_client.patch(reverse("notification-read", args=[first_id])).status_code == 200
    assert api_client.get(reverse("notification-unread-count")).json()["unread"] == 1

    api_client.post(reverse("notification-mark-all-read"))
    assert api_client.get(reverse("notification-unread-count")).json()["unread"] == 0


def test_preferences_get_and_patch(api_client):
    user, _ = make_recruiter("rec@example.com")
    api_client.force_authenticate(user=user)

    matrix = api_client.get(reverse("notification-preferences")).json()["preferences"]
    assert {row["event_type"] for row in matrix} == set(Notification.EventType.values)
    assert all(row["email_enabled"] and row["in_app_enabled"] for row in matrix)

    api_client.patch(
        reverse("notification-preferences"),
        {"preferences": [{"event_type": "candidate_moved", "email_enabled": False}]},
        format="json",
    )
    pref = NotificationPreference.objects.get(
        user=user, event_type=Notification.EventType.CANDIDATE_MOVED
    )
    assert pref.email_enabled is False
    assert pref.in_app_enabled is True


def test_status_move_notifies_job_owner_not_actor(api_client):
    owner, org = make_recruiter("owner@example.com")
    mover, _ = make_recruiter("mover@example.com", organization=org)
    job = make_job(org, owner)
    application = make_application(org, job)

    api_client.force_authenticate(user=mover)
    response = api_client.patch(
        reverse("application-status-update", args=[application.id]),
        {"status": "shortlisted"},
        format="json",
    )

    assert response.status_code == 200
    assert (
        Notification.objects.filter(
            recipient=owner,
            event_type=Notification.EventType.CANDIDATE_MOVED,
        ).count()
        == 1
    )
    assert Notification.objects.filter(recipient=mover).count() == 0


def test_new_application_notifies_job_owner(api_client):
    owner, org = make_recruiter("owner@example.com")
    job = make_job(org, owner)

    response = api_client.post(
        reverse("job-apply", args=[job.id]),
        {
            "first_name": "Bob",
            "last_name": "Jones",
            "email": "bob@example.com",
        },
        format="json",
    )

    assert response.status_code in (200, 201)
    assert Notification.objects.filter(
        recipient=owner,
        event_type=Notification.EventType.NEW_APPLICATION,
    ).exists()
