from django.urls import path

from . import views

urlpatterns = [
    path(
        "applications/<uuid:application_id>/questions/",
        views.ApplicationInterviewQuestionSetView.as_view(),
        name="interview-question-set",
    ),
    path(
        "applications/<uuid:application_id>/generate/",
        views.GenerateInterviewQuestionSetView.as_view(),
        name="interview-question-generate",
    ),
    path(
        "questions/<uuid:pk>/",
        views.InterviewQuestionDetailView.as_view(),
        name="interview-question-detail",
    ),
    path(
        "questions/<uuid:question_id>/notes/",
        views.InterviewQuestionNoteCreateView.as_view(),
        name="interview-question-note-create",
    ),
    path("question-bank/", views.QuestionBankListCreateView.as_view(), name="question-bank-list"),
]
