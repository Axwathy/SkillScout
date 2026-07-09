import uuid

from django.conf import settings
from django.db import models


class InterviewQuestionSet(models.Model):
    class Status(models.TextChoices):
        READY = "ready", "Ready"
        ERROR = "error", "Error"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="interview_question_sets",
    )
    application = models.ForeignKey(
        "candidates.Application",
        on_delete=models.CASCADE,
        related_name="interview_question_sets",
    )
    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="generated_interview_question_sets",
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.READY)
    model = models.CharField(max_length=100, blank=True)
    source_context_hash = models.CharField(max_length=64, db_index=True)
    generation_errors = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["organization", "application", "created_at"]),
            models.Index(fields=["application", "source_context_hash"]),
        ]

    def __str__(self) -> str:
        return f"Interview questions for {self.application_id}"


class InterviewQuestion(models.Model):
    class Category(models.TextChoices):
        TECHNICAL = "technical", "Technical"
        BEHAVIORAL = "behavioral", "Behavioral"
        SITUATIONAL = "situational", "Situational"
        CULTURE_FIT = "culture_fit", "Culture Fit"
        GAP_ANALYSIS = "gap_analysis", "Gap Analysis"

    class Source(models.TextChoices):
        AI = "ai", "AI"
        BANK = "bank", "Question Bank"
        MANUAL = "manual", "Manual"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question_set = models.ForeignKey(
        InterviewQuestionSet,
        on_delete=models.CASCADE,
        related_name="questions",
    )
    category = models.CharField(max_length=30, choices=Category.choices)
    question_text = models.TextField()
    rationale = models.TextField(blank=True)
    evaluation_criteria = models.TextField(blank=True)
    source = models.CharField(max_length=20, choices=Source.choices, default=Source.AI)
    order = models.PositiveSmallIntegerField(default=0)
    is_pinned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "created_at"]
        indexes = [
            models.Index(fields=["question_set", "category", "order"]),
        ]

    def __str__(self) -> str:
        return self.question_text[:80]


class InterviewQuestionNote(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.ForeignKey(
        InterviewQuestion,
        on_delete=models.CASCADE,
        related_name="notes",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="interview_question_notes",
    )
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["question", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"Note for question {self.question_id}"


class QuestionBankItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="question_bank_items",
        null=True,
        blank=True,
    )
    role_family = models.CharField(max_length=100, blank=True)
    category = models.CharField(max_length=30, choices=InterviewQuestion.Category.choices)
    question_text = models.TextField()
    evaluation_criteria = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["role_family", "category", "created_at"]
        indexes = [
            models.Index(fields=["organization", "role_family", "category"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self) -> str:
        return self.question_text[:80]
