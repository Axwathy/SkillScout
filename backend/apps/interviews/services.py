import hashlib
import json
from dataclasses import dataclass
from typing import Any, Literal

import httpx
from django.conf import settings
from django.db.models import Q
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from apps.ai_engine.llm import gemini_generate_text, is_gemini_model
from apps.ai_engine.ranking import extract_candidate_skills, extract_job_skills
from apps.candidates.models import Application, ParsedResume

from .models import InterviewQuestion, InterviewQuestionSet, QuestionBankItem

QuestionCategory = Literal[
    "technical",
    "behavioral",
    "situational",
    "culture_fit",
    "gap_analysis",
]

ALLOWED_CATEGORIES = {
    "technical",
    "behavioral",
    "situational",
    "culture_fit",
    "gap_analysis",
}
DEFAULT_MODEL = "question-bank-fallback"

INTERVIEW_PROMPT = """You are helping a recruiter prepare an interview.
Generate interview questions for the candidate-job pair below.
Return ONLY JSON with no markdown fences.

Rules:
- Do not make hiring recommendations.
- Do not score the candidate.
- Do not ask about protected characteristics, family status, medical status,
  age, religion, nationality, disability, pregnancy, or compensation history.
- Questions must be job-related and evidence-seeking.
- Include evaluation criteria the interviewer can listen for.

Job:
{job_context}

Candidate:
{candidate_context}

Ranking context:
{score_context}

Return JSON exactly like:
{{
  "questions": [
    {{
      "category": "technical"|"behavioral"|"situational"|"culture_fit"|"gap_analysis",
      "question_text": string,
      "rationale": string,
      "evaluation_criteria": string
    }}
  ]
}}
"""

DEFAULT_BANK_QUESTIONS = [
    {
        "role_family": "engineering",
        "category": "technical",
        "question_text": (
            "Walk me through a recent technical problem you solved that is similar to this role."
        ),
        "evaluation_criteria": (
            "Look for clear problem framing, trade-off awareness, and evidence of direct "
            "ownership."
        ),
    },
    {
        "role_family": "engineering",
        "category": "technical",
        "question_text": (
            "Which parts of this job's stack have you used in production, and where would "
            "you need ramp-up time?"
        ),
        "evaluation_criteria": (
            "Listen for honest scope of experience, depth in required tools, and practical "
            "learning plan."
        ),
    },
    {
        "role_family": "general",
        "category": "behavioral",
        "question_text": (
            "Tell me about a time you received critical feedback and changed your approach."
        ),
        "evaluation_criteria": "Look for ownership, reflection, and a concrete behavior change.",
    },
    {
        "role_family": "general",
        "category": "situational",
        "question_text": (
            "If priorities changed halfway through a project, how would you reset "
            "expectations with stakeholders?"
        ),
        "evaluation_criteria": (
            "Look for communication, prioritization, and structured risk management."
        ),
    },
    {
        "role_family": "general",
        "category": "culture_fit",
        "question_text": (
            "What team environment helps you do your best work, and how do you contribute "
            "to that environment?"
        ),
        "evaluation_criteria": (
            "Evaluate collaboration style, self-awareness, and alignment with team norms."
        ),
    },
    {
        "role_family": "general",
        "category": "gap_analysis",
        "question_text": (
            "I noticed some role requirements are not obvious from your resume. Which "
            "related experience should we discuss?"
        ),
        "evaluation_criteria": (
            "Look for transferable experience, clarity about gaps, and learning ability."
        ),
    },
]


class GeneratedQuestion(BaseModel):
    model_config = ConfigDict(extra="ignore")

    category: QuestionCategory
    question_text: str
    rationale: str = ""
    evaluation_criteria: str = ""

    @field_validator("question_text", "rationale", "evaluation_criteria", mode="before")
    @classmethod
    def normalize_text(cls, value: Any) -> str:
        return " ".join(str(value or "").split())


class GeneratedQuestionPayload(BaseModel):
    model_config = ConfigDict(extra="ignore")

    questions: list[GeneratedQuestion] = Field(default_factory=list)


@dataclass(frozen=True)
class GeneratedQuestions:
    questions: list[GeneratedQuestion]
    model: str
    errors: list[str]


def generate_interview_question_set(
    application: Application,
    *,
    user,
    force: bool = False,
) -> InterviewQuestionSet:
    context = build_interview_context(application)
    context_hash = _context_hash(context)
    existing = (
        InterviewQuestionSet.objects.filter(
            application=application,
            organization=application.organization,
            source_context_hash=context_hash,
            status=InterviewQuestionSet.Status.READY,
        )
        .prefetch_related("questions")
        .order_by("-created_at")
        .first()
    )
    if existing and existing.questions.exists() and not force:
        return existing

    generated = _generate_questions(context)
    question_set = InterviewQuestionSet.objects.create(
        organization=application.organization,
        application=application,
        generated_by=user,
        status=InterviewQuestionSet.Status.READY,
        model=generated.model,
        source_context_hash=context_hash,
        generation_errors=generated.errors,
    )
    _create_questions(question_set, generated.questions, generated.model)
    return question_set


def latest_interview_question_set(application: Application) -> InterviewQuestionSet | None:
    return (
        InterviewQuestionSet.objects.filter(
            application=application,
            organization=application.organization,
            status=InterviewQuestionSet.Status.READY,
        )
        .prefetch_related("questions__notes")
        .order_by("-created_at")
        .first()
    )


def build_interview_context(application: Application) -> dict[str, Any]:
    parsed_resume = (
        ParsedResume.objects.filter(
            application=application,
            status=ParsedResume.Status.COMPLETED,
        )
        .order_by("-parsed_at", "-created_at")
        .first()
    )
    candidate_skills = extract_candidate_skills(parsed_resume) if parsed_resume else []
    job_skills = extract_job_skills(application.job)
    missing_skills = [
        skill
        for skill in job_skills
        if _normalize_skill(skill) not in {_normalize_skill(item) for item in candidate_skills}
    ]

    return {
        "organization_id": str(application.organization_id),
        "job": {
            "title": application.job.title,
            "description": application.job.description,
            "requirements": application.job.requirements,
            "location": application.job.location,
            "remote_policy": application.job.remote_policy,
            "employment_type": application.job.employment_type,
            "skills": job_skills,
        },
        "candidate": {
            "name": application.candidate.full_name,
            "email": application.candidate.email,
            "skills": candidate_skills,
            "summary": (parsed_resume.data or {}).get("summary") if parsed_resume else "",
            "experience": (parsed_resume.data or {}).get("experience", []) if parsed_resume else [],
            "projects": (parsed_resume.data or {}).get("projects", []) if parsed_resume else [],
        },
        "score": {
            "semantic_score": _score_value(application.semantic_score),
            "skill_score": _score_value(application.skill_score),
            "experience_score": _score_value(application.experience_score),
            "final_score": _score_value(application.final_score),
            "missing_skills": missing_skills,
        },
    }


def _generate_questions(context: dict[str, Any]) -> GeneratedQuestions:
    errors = []
    for model in _llm_models():
        try:
            payload = _request_llm_questions(context, model)
            questions = _validate_questions(payload)
            if questions:
                return GeneratedQuestions(questions=questions, model=model, errors=errors)
            errors.append(f"{model}: no valid questions returned")
        except (httpx.HTTPError, json.JSONDecodeError, ValidationError, ValueError) as exc:
            errors.append(f"{model}: {exc}")

    return GeneratedQuestions(
        questions=_fallback_questions(context),
        model=DEFAULT_MODEL,
        errors=errors,
    )


def _request_llm_questions(context: dict[str, Any], model: str) -> dict[str, Any]:
    prompt = INTERVIEW_PROMPT.format(
        job_context=json.dumps(context["job"], ensure_ascii=True, default=str)[:6000],
        candidate_context=json.dumps(context["candidate"], ensure_ascii=True, default=str)[:8000],
        score_context=json.dumps(context["score"], ensure_ascii=True, default=str),
    )

    if is_gemini_model(model):
        raw_response, _ = gemini_generate_text(prompt, model, temperature=0.2)
        if not raw_response:
            raise ValueError(f"Model '{model}' returned an empty response.")
        return _parse_json_object(raw_response)

    headers = {}
    if getattr(settings, "OLLAMA_API_KEY", ""):
        headers["Authorization"] = f"Bearer {settings.OLLAMA_API_KEY}"

    response = httpx.post(
        f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/generate",
        headers=headers,
        json={
            "model": model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": 0.2,
                "top_p": 0.7,
                "num_predict": min(getattr(settings, "OLLAMA_NUM_PREDICT", 4096), 4096),
            },
        },
        timeout=getattr(settings, "OLLAMA_TIMEOUT_SECONDS", 120),
    )
    response.raise_for_status()
    body = response.json()
    raw_response = str(body.get("response", "")).strip()
    if not raw_response:
        raise ValueError(f"Model '{model}' returned an empty response.")
    return _parse_json_object(raw_response)


def _validate_questions(payload: dict[str, Any]) -> list[GeneratedQuestion]:
    parsed = GeneratedQuestionPayload.model_validate(payload)
    questions = []
    seen = set()
    for question in parsed.questions:
        text = question.question_text.strip()
        if len(text) < 12:
            continue
        if _contains_blocked_topic(text):
            continue
        key = (question.category, text.lower())
        if key in seen:
            continue
        seen.add(key)
        questions.append(question)
    return questions[:10]


def _fallback_questions(context: dict[str, Any]) -> list[GeneratedQuestion]:
    role_family = _role_family(context["job"]["title"])
    seeded = list(
        QuestionBankItem.objects.filter(
            is_active=True,
        )
        .filter(
            Q(organization_id=context["organization_id"]) | Q(organization__isnull=True),
        ).filter(role_family__in=[role_family, "general", ""])
    )
    source_rows = seeded or [QuestionBankItem(**row) for row in DEFAULT_BANK_QUESTIONS]
    questions = []
    for row in source_rows:
        question_text = row.question_text
        if (
            row.category == InterviewQuestion.Category.GAP_ANALYSIS
            and context["score"]["missing_skills"]
        ):
            question_text = (
                "The resume does not clearly show "
                f"{', '.join(context['score']['missing_skills'][:3])}. "
                "Which related experience should we discuss?"
            )
        questions.append(
            GeneratedQuestion(
                category=row.category,
                question_text=question_text,
                rationale="Fallback question selected from the interview question bank.",
                evaluation_criteria=row.evaluation_criteria,
            )
        )
    return questions[:8]


def _create_questions(
    question_set: InterviewQuestionSet,
    questions: list[GeneratedQuestion],
    model: str,
) -> None:
    source = (
        InterviewQuestion.Source.BANK
        if model == DEFAULT_MODEL
        else InterviewQuestion.Source.AI
    )
    InterviewQuestion.objects.bulk_create(
        [
            InterviewQuestion(
                question_set=question_set,
                category=question.category,
                question_text=question.question_text,
                rationale=question.rationale,
                evaluation_criteria=question.evaluation_criteria,
                source=source,
                order=index,
            )
            for index, question in enumerate(questions, start=1)
        ]
    )


def _llm_models() -> list[str]:
    configured = []
    # Gemini is primary when configured; Ollama models stay as fallback.
    if getattr(settings, "GEMINI_API_KEY", ""):
        configured.append(getattr(settings, "GEMINI_MODEL", "gemini-2.5-flash"))
    configured.append(getattr(settings, "LLM_MODEL", ""))
    configured.extend(getattr(settings, "LLM_FALLBACK_MODELS", []))
    models = []
    for model in configured:
        model = str(model or "").strip()
        if model and model not in models:
            models.append(model)
    return models


def _context_hash(context: dict[str, Any]) -> str:
    serialized = json.dumps(context, sort_keys=True, default=str)
    return hashlib.sha256(serialized.encode()).hexdigest()


def _score_value(value) -> float | None:
    return float(value) if value is not None else None


def _normalize_skill(value: str) -> str:
    return "".join(char.lower() for char in value if char.isalnum() or char in {"+", "#", "."})


def _role_family(title: str) -> str:
    lowered = title.lower()
    if any(term in lowered for term in ["engineer", "developer", "frontend", "backend"]):
        return "engineering"
    if "design" in lowered:
        return "design"
    if "product" in lowered:
        return "product"
    if "sales" in lowered:
        return "sales"
    if "marketing" in lowered:
        return "marketing"
    return "general"


def _contains_blocked_topic(text: str) -> bool:
    lowered = text.lower()
    blocked_terms = [
        "age",
        "religion",
        "pregnant",
        "pregnancy",
        "disability",
        "medical",
        "marital",
        "family status",
        "nationality",
        "citizenship",
        "salary history",
    ]
    return any(term in lowered for term in blocked_terms)


def _parse_json_object(value: str) -> dict[str, Any]:
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        start = value.find("{")
        end = value.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise
        return json.loads(value[start : end + 1])
