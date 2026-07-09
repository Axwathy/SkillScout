from django.contrib import admin

from .models import (
    InterviewQuestion,
    InterviewQuestionNote,
    InterviewQuestionSet,
    QuestionBankItem,
)


class InterviewQuestionInline(admin.TabularInline):
    model = InterviewQuestion
    extra = 0


@admin.register(InterviewQuestionSet)
class InterviewQuestionSetAdmin(admin.ModelAdmin):
    list_display = ("application", "organization", "status", "model", "created_at")
    list_filter = ("status", "model", "created_at")
    search_fields = ("application__candidate__email", "application__job__title")
    inlines = [InterviewQuestionInline]


@admin.register(InterviewQuestion)
class InterviewQuestionAdmin(admin.ModelAdmin):
    list_display = ("question_set", "category", "source", "order", "is_pinned")
    list_filter = ("category", "source", "is_pinned")
    search_fields = ("question_text", "rationale", "evaluation_criteria")


@admin.register(InterviewQuestionNote)
class InterviewQuestionNoteAdmin(admin.ModelAdmin):
    list_display = ("question", "author", "created_at")
    search_fields = ("body", "author__email")


@admin.register(QuestionBankItem)
class QuestionBankItemAdmin(admin.ModelAdmin):
    list_display = ("role_family", "category", "organization", "is_active")
    list_filter = ("category", "is_active", "role_family")
    search_fields = ("question_text", "evaluation_criteria")
