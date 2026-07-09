from django.urls import path

from . import views

urlpatterns = [
    path("", views.BatchHistoryView.as_view(), name="batch-history"),
    path("upload/", views.BulkUploadView.as_view(), name="batch-upload"),
    path("score/<uuid:job_id>/", views.BatchScoreView.as_view(), name="batch-score"),
    path("pipeline-action/", views.PipelineActionView.as_view(), name="batch-pipeline-action"),
    path("<uuid:pk>/", views.BatchDetailView.as_view(), name="batch-detail"),
    path("<uuid:pk>/progress/", views.BatchProgressView.as_view(), name="batch-progress"),
    path("<uuid:pk>/cancel/", views.BatchCancelView.as_view(), name="batch-cancel"),
    path(
        "<uuid:pk>/items/<uuid:item_id>/retry/",
        views.BatchItemRetryView.as_view(),
        name="batch-item-retry",
    ),
    path("schedules/", views.ScheduledBatchListCreateView.as_view(), name="batch-schedule-list"),
    path(
        "schedules/<uuid:pk>/",
        views.ScheduledBatchDetailView.as_view(),
        name="batch-schedule-detail",
    ),
]
