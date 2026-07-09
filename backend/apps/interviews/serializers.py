from rest_framework import serializers

from apps.core.security import sanitize_text

from .models import InterviewQuestion, InterviewQuestionNote, InterviewQuestionSet, QuestionBankItem


class InterviewQuestionNoteSerializer(serializers.ModelSerializer):
    author_email = serializers.EmailField(source="author.email", read_only=True, default=None)

    class Meta:
        model = InterviewQuestionNote
        fields = ("id", "author_email", "body", "created_at", "updated_at")
        read_only_fields = ("id", "author_email", "created_at", "updated_at")


class InterviewQuestionSerializer(serializers.ModelSerializer):
    notes = InterviewQuestionNoteSerializer(many=True, read_only=True)
    category_label = serializers.CharField(source="get_category_display", read_only=True)
    source_label = serializers.CharField(source="get_source_display", read_only=True)

    class Meta:
        model = InterviewQuestion
        fields = (
            "id",
            "category",
            "category_label",
            "question_text",
            "rationale",
            "evaluation_criteria",
            "source",
            "source_label",
            "order",
            "is_pinned",
            "notes",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "category_label",
            "source_label",
            "created_at",
            "updated_at",
        )


class InterviewQuestionSetSerializer(serializers.ModelSerializer):
    questions = InterviewQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = InterviewQuestionSet
        fields = (
            "id",
            "application",
            "status",
            "model",
            "source_context_hash",
            "generation_errors",
            "questions",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class InterviewQuestionUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterviewQuestion
        fields = ("question_text", "rationale", "evaluation_criteria", "order", "is_pinned")

    def validate_question_text(self, value):
        return sanitize_text(value)

    def validate_rationale(self, value):
        return sanitize_text(value)

    def validate_evaluation_criteria(self, value):
        return sanitize_text(value)


class InterviewQuestionNoteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterviewQuestionNote
        fields = ("body",)

    def validate_body(self, value):
        return sanitize_text(value)


class QuestionBankItemSerializer(serializers.ModelSerializer):
    category_label = serializers.CharField(source="get_category_display", read_only=True)

    class Meta:
        model = QuestionBankItem
        fields = (
            "id",
            "role_family",
            "category",
            "category_label",
            "question_text",
            "evaluation_criteria",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "category_label", "created_at", "updated_at")

    def validate_role_family(self, value):
        return sanitize_text(value)

    def validate_question_text(self, value):
        return sanitize_text(value)

    def validate_evaluation_criteria(self, value):
        return sanitize_text(value)
