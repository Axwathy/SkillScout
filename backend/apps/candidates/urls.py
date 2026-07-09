from django.urls import path

from . import views

urlpatterns = [
    # Candidate routes
    path("candidates/", views.CandidateListView.as_view(), name="candidate-list"),
    path(
        "candidates/<uuid:pk>/profile/",
        views.CandidateProfileView.as_view(),
        name="recruiter-candidate-profile",
    ),
    path(
        "candidates/<uuid:pk>/notes/",
        views.CandidateNoteListCreateView.as_view(),
        name="candidate-note-list",
    ),
    path(
        "candidates/<uuid:candidate_id>/notes/<uuid:pk>/",
        views.CandidateNoteDetailView.as_view(),
        name="candidate-note-detail",
    ),
    path("candidates/<uuid:pk>/", views.CandidateDetailView.as_view(), name="candidate-detail"),
    path("candidates/resumes/upload/", views.ResumeUploadView.as_view(), name="resume-upload"),
    
    # Application routes
    path("", views.ApplicationListView.as_view(), name="application-list"),
    path("<uuid:pk>/", views.ApplicationDetailView.as_view(), name="application-detail"),
    path(
        "<uuid:pk>/status/",
        views.ApplicationStatusUpdateView.as_view(),
        name="application-status-update",
    ),
    path("pipeline/", views.PipelineBoardView.as_view(), name="pipeline-board"),
]
