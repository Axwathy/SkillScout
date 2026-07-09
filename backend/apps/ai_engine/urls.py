from django.urls import path

from . import views

urlpatterns = [
    path("", views.SearchAllView.as_view(), name="semantic-search"),
    path("candidates/", views.CandidateSearchView.as_view(), name="semantic-search-candidates"),
    path("jobs/", views.JobSearchView.as_view(), name="semantic-search-jobs"),
]
