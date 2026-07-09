from unittest.mock import patch

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from apps.accounts.models import Recruiter, User
from apps.candidates.models import Application, Candidate, ParsedResume, Resume
from apps.interviews.models import InterviewQuestion, QuestionBankItem
from apps.jobs.models import Job
from apps.organizations.models import Organization

pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client():
    return APIClient()


def create_recruiter(email="recruiter@example.com", org_name="Nexus Talent"):
    user = User.objects.create_user(
        email=email,
        password="StrongPass123!",
        first_name="Rina",
        last_name="Shah",
        role=User.Role.RECRUITER,
    )
    organization = Organization.objects.create(
        name=org_name,
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


def create_application(organization, user):
    job = Job.objects.create(
        organization=organization,
        created_by=user,
        title="Frontend Engineer",
        description="Build accessible React user interfaces.",
        requirements="React TypeScript JavaScript 3 years experience.",
        location="Remote",
    )
    candidate = Candidate.objects.create(
        organization=organization,
        first_name="Asha",
        last_name="Candidate",
        email="asha@example.com",
    )
    application = Application.objects.create(
        candidate=candidate,
        job=job,
        organization=organization,
        semantic_score=0.8,
        skill_score=0.67,
        experience_score=1,
        final_score=0.81,
        score_version="hybrid-v1",
    )
    resume = Resume.objects.create(
        candidate=candidate,
        application=application,
        file_url=f"{organization.id}/{candidate.id}/resume.pdf",
        file_name="resume.pdf",
        file_size=100,
        mime_type="application/pdf",
        status=Resume.Status.COMPLETED,
    )
    ParsedResume.objects.create(
        resume=resume,
        candidate=candidate,
        application=application,
        status=ParsedResume.Status.COMPLETED,
        data={
            "summary": "Frontend engineer with React experience.",
            "skills": [{"name": "React"}, {"name": "TypeScript"}],
            "_metadata": {"total_years_experience": 4},
        },
        confidence=ParsedResume.Confidence.HIGH,
    )
    return application


def test_generate_interview_questions_with_llm(api_client):
    user, organization = create_recruiter()
    application = create_application(organization, user)
    api_client.force_authenticate(user=user)

    with patch(
        "apps.interviews.services._request_llm_questions",
        return_value={
            "questions": [
                {
                    "category": "technical",
                    "question_text": (
                        "How have you structured React components for maintainability?"
                    ),
                    "rationale": "Tests role-specific frontend depth.",
                    "evaluation_criteria": (
                        "Look for component boundaries and state management trade-offs."
                    ),
                }
            ]
        },
    ):
        response = api_client.post(
            reverse("interview-question-generate", args=[application.id])
        )

    assert response.status_code == 201
    payload = response.json()["question_set"]
    assert payload["application"] == str(application.id)
    assert payload["model"]
    assert len(payload["questions"]) == 1
    assert payload["questions"][0]["category"] == InterviewQuestion.Category.TECHNICAL
    assert application.final_score is not None
    application.refresh_from_db()
    assert application.status == Application.Status.APPLIED


def test_generate_interview_questions_falls_back_to_bank(api_client):
    user, organization = create_recruiter()
    application = create_application(organization, user)
    QuestionBankItem.objects.create(
        role_family="engineering",
        category=InterviewQuestion.Category.TECHNICAL,
        question_text="Which React performance issue have you diagnosed recently?",
        evaluation_criteria="Listen for profiling and measurable improvements.",
    )
    api_client.force_authenticate(user=user)

    with patch(
        "apps.interviews.services._request_llm_questions",
        side_effect=ValueError("LLM unavailable"),
    ):
        response = api_client.post(
            reverse("interview-question-generate", args=[application.id])
        )

    assert response.status_code == 201
    payload = response.json()["question_set"]
    assert payload["model"] == "question-bank-fallback"
    assert payload["generation_errors"]
    assert payload["questions"][0]["source"] == InterviewQuestion.Source.BANK


def test_interview_questions_are_tenant_scoped(api_client):
    user, organization = create_recruiter()
    other_user, other_org = create_recruiter("other@example.com", "Other Org")
    application = create_application(organization, user)
    api_client.force_authenticate(user=other_user)

    response = api_client.get(reverse("interview-question-set", args=[application.id]))

    assert response.status_code == 404
    assert other_org.id != organization.id


def test_question_note_create(api_client):
    user, organization = create_recruiter()
    application = create_application(organization, user)
    api_client.force_authenticate(user=user)

    with patch(
        "apps.interviews.services._request_llm_questions",
        return_value={
            "questions": [
                {
                    "category": "behavioral",
                    "question_text": "Tell me about a time you improved a team process.",
                    "rationale": "Tests collaboration.",
                    "evaluation_criteria": "Look for ownership and measurable impact.",
                }
            ]
        },
    ):
        response = api_client.post(reverse("interview-question-generate", args=[application.id]))
    question_id = response.json()["question_set"]["questions"][0]["id"]

    note_response = api_client.post(
        reverse("interview-question-note-create", args=[question_id]),
        {"body": "Candidate gave a clear STAR answer."},
        format="json",
    )

    assert note_response.status_code == 201
    assert note_response.json()["body"] == "Candidate gave a clear STAR answer."


def test_question_bank_list_includes_global_and_org_items(api_client):
    user, organization = create_recruiter()
    QuestionBankItem.objects.create(
        role_family="general",
        category=InterviewQuestion.Category.BEHAVIORAL,
        question_text="Global question",
        evaluation_criteria="Global criteria",
    )
    QuestionBankItem.objects.create(
        organization=organization,
        role_family="engineering",
        category=InterviewQuestion.Category.TECHNICAL,
        question_text="Organization question",
        evaluation_criteria="Org criteria",
    )
    api_client.force_authenticate(user=user)

    response = api_client.get(reverse("question-bank-list"))

    assert response.status_code == 200
    texts = {item["question_text"] for item in response.json()}
    assert {"Global question", "Organization question"}.issubset(texts)
