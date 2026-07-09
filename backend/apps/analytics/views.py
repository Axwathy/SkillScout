from django.http import HttpResponse
from rest_framework import generics, status, views
from rest_framework.response import Response

from apps.accounts.permissions import IsVerifiedRecruiter
from apps.candidates.views import get_recruiter_organization
from apps.jobs.models import Job

from . import services


class AnalyticsOverviewView(views.APIView):
    permission_classes = [IsVerifiedRecruiter]

    def get(self, request, *args, **kwargs):
        organization = get_recruiter_organization(request)
        start, end = services.parse_date_range(request.query_params)
        return Response(
            services.cached_metric(
                "overview",
                organization,
                lambda: services.compute_overview(organization, start=start, end=end),
                start=start,
                end=end,
            )
        )


class AnalyticsFunnelView(views.APIView):
    permission_classes = [IsVerifiedRecruiter]

    def get(self, request, *args, **kwargs):
        organization = get_recruiter_organization(request)
        start, end = services.parse_date_range(request.query_params)

        job = None
        job_id = request.query_params.get("job")
        if job_id:
            job = generics.get_object_or_404(Job, pk=job_id, organization=organization)

        return Response(
            services.cached_metric(
                "funnel",
                organization,
                lambda: services.compute_funnel(organization, job=job, start=start, end=end),
                start=start,
                end=end,
                extra=str(job.id) if job else "",
            )
        )


class AnalyticsTimeToHireView(views.APIView):
    permission_classes = [IsVerifiedRecruiter]

    def get(self, request, *args, **kwargs):
        organization = get_recruiter_organization(request)
        start, end = services.parse_date_range(request.query_params)
        return Response(
            services.cached_metric(
                "time-to-hire",
                organization,
                lambda: services.compute_time_to_hire(organization, start=start, end=end),
                start=start,
                end=end,
            )
        )


class AnalyticsDashboardView(views.APIView):
    permission_classes = [IsVerifiedRecruiter]

    def get(self, request, *args, **kwargs):
        organization = get_recruiter_organization(request)
        start, end = services.parse_date_range(request.query_params)
        return Response(services.compute_dashboard(organization, start=start, end=end))


class AnalyticsSourcesView(views.APIView):
    permission_classes = [IsVerifiedRecruiter]

    def get(self, request, *args, **kwargs):
        organization = get_recruiter_organization(request)
        start, end = services.parse_date_range(request.query_params)
        return Response(
            services.cached_metric(
                "sources",
                organization,
                lambda: services.compute_source_effectiveness(organization, start=start, end=end),
                start=start,
                end=end,
            )
        )


class AnalyticsTeamActivityView(views.APIView):
    permission_classes = [IsVerifiedRecruiter]

    def get(self, request, *args, **kwargs):
        organization = get_recruiter_organization(request)
        start, end = services.parse_date_range(request.query_params)
        return Response(
            services.cached_metric(
                "team-activity",
                organization,
                lambda: services.compute_team_activity(organization, start=start, end=end),
                start=start,
                end=end,
            )
        )


class AnalyticsExportView(views.APIView):
    permission_classes = [IsVerifiedRecruiter]

    def get(self, request, *args, **kwargs):
        organization = get_recruiter_organization(request)
        start, end = services.parse_date_range(request.query_params)
        metric = request.query_params.get("metric", "overview")
        try:
            body = services.export_csv(metric, organization, start=start, end=end)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        response = HttpResponse(body, content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="analytics-{metric}.csv"'
        return response


class AnalyticsSnapshotView(views.APIView):
    permission_classes = [IsVerifiedRecruiter]

    def post(self, request, *args, **kwargs):
        organization = get_recruiter_organization(request)
        snapshot_date = services.parse_date_range({"start": request.data.get("date")})[0]
        snapshot = services.create_daily_snapshot(
            organization,
            snapshot_date=snapshot_date.date() if snapshot_date else None,
        )
        return Response(
            {
                "id": str(snapshot.id),
                "snapshot_date": snapshot.snapshot_date.isoformat(),
                "created_at": snapshot.created_at,
                "updated_at": snapshot.updated_at,
            },
            status=status.HTTP_201_CREATED,
        )
