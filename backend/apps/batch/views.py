import logging
import threading

from django.conf import settings
from django.db import close_old_connections
from django.utils.dateparse import parse_datetime
from django.utils.timezone import is_naive, make_aware
from rest_framework import generics, status, views
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response

from apps.accounts.permissions import IsVerifiedRecruiter
from apps.candidates.models import Application
from apps.candidates.views import get_recruiter_organization
from apps.jobs.models import Job

from .models import BatchItem, BatchJob, ScheduledBatchOperation
from .serializers import (
    BatchJobSerializer,
    BatchProgressSerializer,
    ScheduledBatchOperationSerializer,
)
from .services import (
    create_batch_job,
    create_scheduled_operation,
    progress_payload,
    request_cancel_batch,
    stage_uploaded_file,
)
from .tasks import (
    build_score_batch_items,
    retry_batch_item,
    run_batch_score,
    run_bulk_pipeline_action,
    run_bulk_upload,
)

logger = logging.getLogger(__name__)


def dispatch_task(task, *args):
    if getattr(settings, "CELERY_TASK_ALWAYS_EAGER", False):
        if getattr(settings, "BATCH_TASK_RUN_INLINE", False):
            task(*args)
            return

        def run_in_background():
            close_old_connections()
            try:
                task(*args)
            except Exception:
                logger.exception("Background batch task failed: %s", getattr(task, "name", task))
            finally:
                close_old_connections()

        thread = threading.Thread(target=run_in_background, daemon=True)
        thread.start()
        return
    task.delay(*args)


class BatchHistoryView(generics.ListAPIView):
    serializer_class = BatchJobSerializer
    permission_classes = [IsVerifiedRecruiter]

    def get_queryset(self):
        organization = get_recruiter_organization(self.request)
        return BatchJob.objects.filter(organization=organization).select_related("initiated_by")


class BatchDetailView(generics.RetrieveAPIView):
    serializer_class = BatchProgressSerializer
    permission_classes = [IsVerifiedRecruiter]

    def get_queryset(self):
        organization = get_recruiter_organization(self.request)
        return (
            BatchJob.objects.filter(organization=organization)
            .select_related("initiated_by")
            .prefetch_related("items")
        )


class BatchProgressView(views.APIView):
    permission_classes = [IsVerifiedRecruiter]

    def get(self, request, pk, *args, **kwargs):
        organization = get_recruiter_organization(request)
        batch = generics.get_object_or_404(BatchJob, pk=pk, organization=organization)
        return Response(progress_payload(batch))


class BatchCancelView(views.APIView):
    permission_classes = [IsVerifiedRecruiter]

    def post(self, request, pk, *args, **kwargs):
        organization = get_recruiter_organization(request)
        batch = generics.get_object_or_404(BatchJob, pk=pk, organization=organization)
        request_cancel_batch(batch, canceled_by=request.user)
        return Response(progress_payload(batch))


class BulkUploadView(views.APIView):
    permission_classes = [IsVerifiedRecruiter]
    parser_classes = [MultiPartParser, FormParser]
    throttle_scope = "upload"

    def post(self, request, *args, **kwargs):
        organization = get_recruiter_organization(request)
        job = generics.get_object_or_404(
            Job,
            pk=request.data.get("job_id"),
            organization=organization,
        )
        files = request.FILES.getlist("files") or request.FILES.getlist("file")
        if not files:
            return Response(
                {"detail": "At least one resume file is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        staged = [stage_uploaded_file(file) for file in files]
        try:
            batch = create_batch_job(
                organization=organization,
                initiated_by=request.user,
                job_type=BatchJob.JobType.UPLOAD,
                params={"job_id": str(job.id), "job_title": job.title},
                item_labels=[upload.file_name for upload in staged],
                item_metadata=[
                    {
                        "file_name": upload.file_name,
                        "content_type": upload.content_type,
                        "file_size": upload.size,
                        "data_b64": upload.data_b64,
                    }
                    for upload in staged
                ],
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        dispatch_task(run_bulk_upload, str(batch.id))
        return Response(progress_payload(batch), status=status.HTTP_201_CREATED)


class BatchScoreView(views.APIView):
    permission_classes = [IsVerifiedRecruiter]
    parser_classes = [JSONParser]

    def post(self, request, job_id, *args, **kwargs):
        organization = get_recruiter_organization(request)
        job = generics.get_object_or_404(Job, pk=job_id, organization=organization)
        try:
            batch = create_batch_job(
                organization=organization,
                initiated_by=request.user,
                job_type=BatchJob.JobType.SCORE,
                params={"job_id": str(job.id), "job_title": job.title},
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        build_score_batch_items(batch, job)
        dispatch_task(run_batch_score, str(batch.id), str(job.id))
        batch.refresh_from_db()
        return Response(progress_payload(batch), status=status.HTTP_201_CREATED)


class PipelineActionView(views.APIView):
    permission_classes = [IsVerifiedRecruiter]
    parser_classes = [JSONParser]

    def post(self, request, *args, **kwargs):
        organization = get_recruiter_organization(request)
        action = request.data.get("action")
        if action not in {"move", "reject", "archive"}:
            return Response(
                {"detail": "Unsupported batch action."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        application_ids = request.data.get("application_ids") or []
        applications = list(
            Application.objects.filter(id__in=application_ids, organization=organization)
            .select_related("candidate", "job")
            .order_by("candidate__last_name", "candidate__first_name")
        )
        if len(applications) != len(set(str(value) for value in application_ids)):
            return Response(
                {"detail": "One or more applications were not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not applications:
            return Response(
                {"detail": "Select at least one application."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        params = {
            "action": action,
            "target_status": request.data.get("target_status") or "",
            "target_stage_id": request.data.get("target_stage_id") or "",
        }
        try:
            batch = create_batch_job(
                organization=organization,
                initiated_by=request.user,
                job_type=BatchJob.JobType.PIPELINE_ACTION,
                params=params,
                item_labels=[
                    application.candidate.full_name or application.candidate.email
                    for application in applications
                ],
                item_metadata=[
                    {"application_id": str(application.id)}
                    for application in applications
                ],
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        item_pairs = zip(batch.items.order_by("created_at"), applications, strict=False)
        for item, application in item_pairs:
            item.application = application
            item.candidate = application.candidate
            item.save(update_fields=["application", "candidate"])
        dispatch_task(run_bulk_pipeline_action, str(batch.id))
        return Response(progress_payload(batch), status=status.HTTP_201_CREATED)


class BatchItemRetryView(views.APIView):
    permission_classes = [IsVerifiedRecruiter]

    def post(self, request, pk, item_id, *args, **kwargs):
        organization = get_recruiter_organization(request)
        item = generics.get_object_or_404(
            BatchItem.objects.select_related("batch"),
            pk=item_id,
            batch_id=pk,
            batch__organization=organization,
            status=BatchItem.Status.FAILED,
        )
        item.status = BatchItem.Status.PENDING
        item.error = ""
        item.completed_at = None
        item.save(update_fields=["status", "error", "completed_at", "updated_at"])
        dispatch_task(retry_batch_item, str(item.id))
        return Response(progress_payload(item.batch))


class ScheduledBatchListCreateView(views.APIView):
    permission_classes = [IsVerifiedRecruiter]
    parser_classes = [JSONParser]

    def get(self, request, *args, **kwargs):
        organization = get_recruiter_organization(request)
        schedules = ScheduledBatchOperation.objects.filter(organization=organization)
        return Response(ScheduledBatchOperationSerializer(schedules, many=True).data)

    def post(self, request, *args, **kwargs):
        organization = get_recruiter_organization(request)
        job_type = request.data.get("job_type")
        params = request.data.get("params") or {}
        frequency = request.data.get("frequency") or ScheduledBatchOperation.Frequency.ONCE
        run_at = parse_datetime(request.data.get("next_run_at") or "")
        if run_at is None:
            return Response({"detail": "next_run_at must be an ISO datetime."}, status=400)
        if is_naive(run_at):
            run_at = make_aware(run_at)
        if job_type not in {BatchJob.JobType.SCORE, BatchJob.JobType.PIPELINE_ACTION}:
            return Response(
                {"detail": "Only batch score and pipeline actions can be scheduled."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if frequency not in ScheduledBatchOperation.Frequency.values:
            return Response(
                {"detail": "Unsupported frequency."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            schedule = create_scheduled_operation(
                organization=organization,
                created_by=request.user,
                job_type=job_type,
                params=params,
                frequency=frequency,
                next_run_at=run_at,
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            ScheduledBatchOperationSerializer(schedule).data,
            status=status.HTTP_201_CREATED,
        )


class ScheduledBatchDetailView(views.APIView):
    permission_classes = [IsVerifiedRecruiter]

    def delete(self, request, pk, *args, **kwargs):
        organization = get_recruiter_organization(request)
        schedule = generics.get_object_or_404(
            ScheduledBatchOperation,
            pk=pk,
            organization=organization,
        )
        schedule.is_active = False
        schedule.save(update_fields=["is_active", "updated_at"])
        return Response(status=status.HTTP_204_NO_CONTENT)
