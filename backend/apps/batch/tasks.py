import logging

from celery import chord, group, shared_task
from django.conf import settings

from apps.candidates.models import Application
from apps.jobs.models import Job

from .models import BatchItem, BatchJob
from .services import (
    fail_batch,
    finalize_canceled_batch,
    mark_item_failed,
    mark_item_running,
    mark_schedule_ran,
    process_pipeline_item,
    process_score_item,
    process_upload_item,
    refresh_batch_counts,
    should_cancel,
    start_batch,
)

logger = logging.getLogger(__name__)


@shared_task
def run_bulk_upload(batch_id: str) -> None:
    batch = BatchJob.objects.select_related("organization", "initiated_by").get(id=batch_id)
    try:
        start_batch(batch)
        if dispatch_chord_if_available(batch):
            return
        run_batch_items_sequentially(batch, process_upload_item)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Bulk upload batch %s failed", batch_id)
        fail_batch(batch, exc)


@shared_task
def run_batch_score(batch_id: str, job_id: str) -> None:
    batch = BatchJob.objects.select_related("organization", "initiated_by").get(id=batch_id)
    try:
        Job.objects.get(id=job_id, organization=batch.organization)
        start_batch(batch)
        if dispatch_chord_if_available(batch):
            return
        run_batch_items_sequentially(batch, process_score_item)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Batch score job %s failed", batch_id)
        fail_batch(batch, exc)


@shared_task
def run_bulk_pipeline_action(batch_id: str) -> None:
    batch = BatchJob.objects.select_related("organization", "initiated_by").get(id=batch_id)
    try:
        start_batch(batch)
        if dispatch_chord_if_available(batch):
            return
        run_batch_items_sequentially(batch, process_pipeline_item)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Pipeline action batch %s failed", batch_id)
        fail_batch(batch, exc)


@shared_task
def retry_batch_item(item_id: str) -> None:
    item = BatchItem.objects.select_related(
        "batch",
        "batch__organization",
        "batch__initiated_by",
    ).get(id=item_id)
    batch = item.batch
    if batch.job_type == BatchJob.JobType.UPLOAD:
        _process_item(item, process_upload_item)
    elif batch.job_type == BatchJob.JobType.SCORE:
        _process_item(item, process_score_item)
    elif batch.job_type == BatchJob.JobType.PIPELINE_ACTION:
        _process_item(item, process_pipeline_item)
    refresh_batch_counts(batch, finalize=True)


@shared_task
def process_batch_item(item_id: str) -> str:
    item = BatchItem.objects.select_related(
        "batch",
        "batch__organization",
        "batch__initiated_by",
    ).get(id=item_id)
    if should_cancel(item.batch):
        mark_item_failed(item, "Canceled before processing.")
        return "canceled"
    if item.batch.job_type == BatchJob.JobType.UPLOAD:
        _process_item(item, process_upload_item)
    elif item.batch.job_type == BatchJob.JobType.SCORE:
        _process_item(item, process_score_item)
    elif item.batch.job_type == BatchJob.JobType.PIPELINE_ACTION:
        _process_item(item, process_pipeline_item)
    return item.status


@shared_task
def finalize_batch_items(results, batch_id: str) -> None:
    batch = BatchJob.objects.get(id=batch_id)
    if should_cancel(batch):
        finalize_canceled_batch(batch)
        return
    refresh_batch_counts(batch, finalize=True)


@shared_task
def process_due_scheduled_batches() -> int:
    from django.utils import timezone

    from .models import ScheduledBatchOperation
    from .services import create_batch_job

    due = ScheduledBatchOperation.objects.filter(
        is_active=True,
        next_run_at__lte=timezone.now(),
    ).select_related("organization", "created_by")
    launched = 0
    for schedule in due:
        try:
            if schedule.job_type == BatchJob.JobType.SCORE:
                job = Job.objects.get(
                    id=schedule.params["job_id"],
                    organization=schedule.organization,
                )
                batch = create_batch_job(
                    organization=schedule.organization,
                    initiated_by=schedule.created_by,
                    job_type=BatchJob.JobType.SCORE,
                    params={"job_id": str(job.id), "job_title": job.title, "scheduled": True},
                )
                build_score_batch_items(batch, job)
                run_batch_score.delay(str(batch.id), str(job.id))
            elif schedule.job_type == BatchJob.JobType.PIPELINE_ACTION:
                application_ids = schedule.params.get("application_ids") or []
                applications = list(
                    Application.objects.filter(
                        id__in=application_ids,
                        organization=schedule.organization,
                    ).select_related("candidate")
                )
                batch = create_batch_job(
                    organization=schedule.organization,
                    initiated_by=schedule.created_by,
                    job_type=BatchJob.JobType.PIPELINE_ACTION,
                    params={**schedule.params, "scheduled": True},
                    item_labels=[
                        application.candidate.full_name or application.candidate.email
                        for application in applications
                    ],
                    item_metadata=[
                        {"application_id": str(application.id)}
                        for application in applications
                    ],
                )
                run_bulk_pipeline_action.delay(str(batch.id))
            else:
                continue
            mark_schedule_ran(schedule, batch)
            launched += 1
        except Exception as exc:  # noqa: BLE001
            logger.warning("Scheduled batch %s failed to launch: %s", schedule.id, exc)
    return launched


def build_score_batch_items(batch: BatchJob, job: Job) -> None:
    applications = (
        Application.objects.filter(job=job, organization=batch.organization)
        .select_related("candidate")
    )
    items = [
        BatchItem(
            batch=batch,
            label=application.candidate.full_name or application.candidate.email,
            application=application,
            candidate=application.candidate,
            metadata={"application_id": str(application.id)},
        )
        for application in applications
    ]
    BatchItem.objects.bulk_create(items)
    batch.total_count = len(items)
    batch.save(update_fields=["total_count"])


def dispatch_chord_if_available(batch: BatchJob) -> bool:
    if getattr(settings, "CELERY_TASK_ALWAYS_EAGER", False):
        return False
    item_ids = list(batch.items.order_by("created_at").values_list("id", flat=True))
    if not item_ids:
        refresh_batch_counts(batch, finalize=True)
        return True
    header = group(process_batch_item.s(str(item_id)) for item_id in item_ids)
    chord(header)(finalize_batch_items.s(str(batch.id)))
    return True


def run_batch_items_sequentially(batch: BatchJob, processor) -> None:
    for item in batch.items.order_by("created_at"):
        if should_cancel(batch):
            finalize_canceled_batch(batch)
            return
        _process_item(item, processor)
    refresh_batch_counts(batch, finalize=True)


def _process_item(item: BatchItem, processor) -> None:
    item.refresh_from_db()
    mark_item_running(item)
    try:
        processor(item)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Batch item %s failed: %s", item.id, exc)
        mark_item_failed(item, exc)
