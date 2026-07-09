from django.urls import path

from . import views

urlpatterns = [
    path("dashboard/", views.AnalyticsDashboardView.as_view(), name="analytics-dashboard"),
    path("overview/", views.AnalyticsOverviewView.as_view(), name="analytics-overview"),
    path("funnel/", views.AnalyticsFunnelView.as_view(), name="analytics-funnel"),
    path("time-to-hire/", views.AnalyticsTimeToHireView.as_view(), name="analytics-time-to-hire"),
    path("sources/", views.AnalyticsSourcesView.as_view(), name="analytics-sources"),
    path(
        "team-activity/",
        views.AnalyticsTeamActivityView.as_view(),
        name="analytics-team-activity",
    ),
    path("export/", views.AnalyticsExportView.as_view(), name="analytics-export"),
    path("snapshots/", views.AnalyticsSnapshotView.as_view(), name="analytics-snapshot-create"),
]
