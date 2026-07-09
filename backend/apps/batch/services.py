import base64
import hashlib
import logging
import re
from dataclasses import dataclass
from datetime import timedelta
from typing import Any

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from apps.ai_engine.ranking import score_application
from apps.candidates.models import Application, Candidate, ParsedResume, Resume
from apps.candidates.resume_parser import ParseResult, parse_resume_text
from apps.candidates.tasks import extract_text_from_bytes
from apps.core.security import validate_resume_bytes, validate_resume_upload
from apps.core.storage import upload_file
from apps.jobs.models import Job
from apps.pipeline.models import PipelineStage
from apps.pipeline.services import get_stage_for_status, move_application_to_stage

from .models import BatchItem, BatchJob, ScheduledBatchOperation, mark_batch_started
from .serializers import BatchProgressSerializer

logger = logging.getLogger(__name__)

SUPPORTED_UPLOAD_TYPES = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}

ACTIVE_BATCH_STATUSES = {
    BatchJob.Status.PENDING,
    BatchJob.Status.RUNNING,
    BatchJob.Status.CANCEL_REQUESTED,
}
CANCELABLE_BATCH_STATUSES = {BatchJob.Status.PENDING, BatchJob.Status.RUNNING}


@dataclass(frozen=True)
class StagedUpload:
    file_name: str
    content_type: str
    size: int
    data_b64: str


def create_batch_job(
    *,
    organization,
    initiated_by,
    job_type: str,
    params: dict[str, Any] | None = None,
    item_labels: list[str] | None = None,
    item_metadata: list[dict[str, Any]] | None = None,
) -> BatchJob:
    enforce_concurrent_batch_limit(organization)
    labels = item_labels or []
    metadata = item_metadata or [{} for _label in labels]
    with transaction.atomic():
        batch = BatchJob.objects.create(
            organization=organization,
            initiated_by=initiated_by if getattr(initiated_by, "is_authenticated", False) else None,
            job_type=job_type,
            total_count=len(labels),
            params=params or {},
        )
        BatchItem.objects.bulk_create(
            BatchItem(batch=batch, label=label, metadata=metadata[index])
            for index, label in enumerate(labels)
        )
    broadcast_progress(batch)
    return batch


def enforce_concurrent_batch_limit(organization) -> None:
    limit = int(getattr(settings, "BATCH_MAX_ACTIVE_PER_ORG", 3))
    active_count = BatchJob.objects.filter(
        organization=organization,
        status__in=ACTIVE_BATCH_STATUSES,
    ).count()
    if active_count >= limit:
        raise ValueError(
            f"Organization already has {active_count} active batch operation(s). "
            f"Limit is {limit}."
        )


def stage_uploaded_file(file) -> StagedUpload:
    validate_resume_upload(file)
    file_bytes = file.read()
    file.seek(0)
    return StagedUpload(
        file_name=file.name,
        content_type=file.content_type,
        size=file.size,
        data_b64=base64.b64encode(file_bytes).decode("ascii"),
    )


def progress_payload(batch: BatchJob) -> dict[str, Any]:
    fresh = (
        BatchJob.objects.filter(pk=batch.pk)
        .select_related("initiated_by")
        .prefetch_related("items")
        .get()
    )
    return BatchProgressSerializer(fresh).data


def broadcast_progress(batch: BatchJob) -> None:
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return
    try:
        async_to_sync(channel_layer.group_send)(
            f"batch_{batch.id}",
            {"type": "batch.progress", "payload": progress_payload(batch)},
        )
    except Exception as exc:  # noqa: BLE001
        logger.debug("Batch progress broadcast skipped for %s: %s", batch.id, exc)


def start_batch(batch: BatchJob) -> BatchJob:
    batch = mark_batch_started(batch)
    broadcast_progress(batch)
    return batch


def mark_item_running(item: BatchItem) -> BatchItem:
    item.status = BatchItem.Status.RUNNING
    item.error = ""
    item.started_at = timezone.now()
    item.completed_at = None
    item.save(update_fields=["status", "error", "started_at", "completed_at", "updated_at"])
    broadcast_progress(item.batch)
    return item


def mark_item_completed(
    item: BatchItem,
    *,
    application: Application | None = None,
    candidate: Candidate | None = None,
    metadata: dict[str, Any] | None = None,
) -> BatchItem:
    item.status = BatchItem.Status.COMPLETED
    item.error = ""
    item.completed_at = timezone.now()
    if application:
        item.application = application
    if candidate:
        item.candidate = candidate
    if metadata:
        clean_metadata = {**item.metadata, **metadata}
        clean_metadata.pop("data_b64", None)
        item.metadata = clean_metadata
    else:
        item.metadata.pop("data_b64", None)
    item.save(
        update_fields=[
            "status",
            "error",
            "completed_at",
            "application",
            "candidate",
            "metadata",
            "updated_at",
        ]
    )
    refresh_batch_counts(item.batch)
    return item


def mark_item_failed(item: BatchItem, error: Exception | str) -> BatchItem:
    item.status = BatchItem.Status.FAILED
    item.error = str(error)
    item.completed_at = timezone.now()
    item.save(update_fields=["status", "error", "completed_at", "updated_at"])
    refresh_batch_counts(item.batch)
    return item


def refresh_batch_counts(batch: BatchJob, *, finalize: bool = False) -> BatchJob:
    batch.refresh_from_db(fields=["status"])
    counts = batch.items.values("status")
    processed = 0
    failed = 0
    for row in counts:
        if row["status"] in {BatchItem.Status.COMPLETED, BatchItem.Status.FAILED}:
            processed += 1
        if row["status"] == BatchItem.Status.FAILED:
            failed += 1

    batch.processed_count = processed
    batch.failed_count = failed
    if batch.status == BatchJob.Status.CANCEL_REQUESTED:
        batch.completed_at = timezone.now()
        batch.status = BatchJob.Status.CANCELED
    elif finalize or processed >= batch.total_count:
        batch.completed_at = timezone.now()
        batch.status = (
            BatchJob.Status.COMPLETED
            if failed == 0
            else BatchJob.Status.COMPLETED_WITH_ERRORS
        )
    batch.save(
        update_fields=[
            "processed_count",
            "failed_count",
            "status",
            "completed_at",
        ]
    )
    broadcast_progress(batch)
    return batch


def fail_batch(batch: BatchJob, error: Exception | str) -> BatchJob:
    batch.status = BatchJob.Status.FAILED
    batch.completed_at = timezone.now()
    batch.result = {**batch.result, "error": str(error)}
    batch.save(update_fields=["status", "completed_at", "result"])
    broadcast_progress(batch)
    return batch


def request_cancel_batch(batch: BatchJob, *, canceled_by=None) -> BatchJob:
    if batch.status not in CANCELABLE_BATCH_STATUSES:
        return batch

    batch.status = BatchJob.Status.CANCEL_REQUESTED
    batch.result = {
        **(batch.result or {}),
        "cancel_requested_at": timezone.now().isoformat(),
        "cancel_requested_by": str(canceled_by.id) if getattr(canceled_by, "id", None) else None,
    }
    batch.save(update_fields=["status", "result"])
    broadcast_progress(batch)
    return batch


def should_cancel(batch: BatchJob) -> bool:
    batch.refresh_from_db(fields=["status"])
    return batch.status == BatchJob.Status.CANCEL_REQUESTED


def finalize_canceled_batch(batch: BatchJob) -> BatchJob:
    for item in batch.items.filter(status=BatchItem.Status.PENDING):
        item.status = BatchItem.Status.FAILED
        item.error = "Canceled before processing."
        item.completed_at = timezone.now()
        item.save(update_fields=["status", "error", "completed_at", "updated_at"])
    return refresh_batch_counts(batch, finalize=True)


def create_scheduled_operation(
    *,
    organization,
    created_by,
    job_type: str,
    params: dict[str, Any],
    next_run_at,
    frequency: str = ScheduledBatchOperation.Frequency.ONCE,
) -> ScheduledBatchOperation:
    if job_type == BatchJob.JobType.UPLOAD:
        raise ValueError(
            "Bulk upload cannot be scheduled because uploaded files are request-bound."
        )
    return ScheduledBatchOperation.objects.create(
        organization=organization,
        created_by=created_by if getattr(created_by, "is_authenticated", False) else None,
        job_type=job_type,
        params=params,
        frequency=frequency,
        next_run_at=next_run_at,
    )


def mark_schedule_ran(
    schedule: ScheduledBatchOperation,
    batch: BatchJob,
) -> ScheduledBatchOperation:
    schedule.last_batch = batch
    schedule.last_run_at = timezone.now()
    if schedule.frequency == ScheduledBatchOperation.Frequency.ONCE:
        schedule.is_active = False
    elif schedule.frequency == ScheduledBatchOperation.Frequency.DAILY:
        schedule.next_run_at = schedule.next_run_at + timedelta(days=1)
    elif schedule.frequency == ScheduledBatchOperation.Frequency.WEEKLY:
        schedule.next_run_at = schedule.next_run_at + timedelta(days=7)
    schedule.save(
        update_fields=[
            "last_batch",
            "last_run_at",
            "is_active",
            "next_run_at",
            "updated_at",
        ]
    )
    return schedule


def process_upload_item(item: BatchItem) -> BatchItem:
    batch = item.batch
    metadata = item.metadata or {}
    file_bytes = base64.b64decode(metadata["data_b64"])
    file_name = metadata["file_name"]
    content_type = metadata["content_type"]
    validate_resume_bytes(file_bytes, file_name=file_name, content_type=content_type)

    job = Job.objects.select_related("organization").get(
        id=batch.params["job_id"],
        organization=batch.organization,
    )
    raw_text = extract_text_from_bytes(file_bytes, content_type)
    parsed = parse_resume_text(raw_text)
    candidate, placeholder = resolve_candidate_from_parse(
        organization=batch.organization,
        parsed=parsed,
        file_name=file_name,
    )
    application, _created = Application.objects.get_or_create(
        candidate=candidate,
        job=job,
        defaults={
            "organization": batch.organization,
            "source": Application.Source.DIRECT,
        },
    )
    if not application.current_stage:
        application.current_stage = get_stage_for_status(job, application.status)
        application.save(update_fields=["current_stage", "updated_at"])

    resume = persist_uploaded_resume(
        application=application,
        file_name=file_name,
        file_bytes=file_bytes,
        content_type=content_type,
        uploaded_by=batch.initiated_by,
    )
    persist_parsed_resume(
        resume=resume,
        application=application,
        candidate=candidate,
        raw_text=raw_text,
        parsed=parsed,
    )
    score_application(application, force=True)

    return mark_item_completed(
        item,
        application=application,
        candidate=candidate,
        metadata={
            "file_name": file_name,
            "content_type": content_type,
            "file_size": metadata.get("file_size", len(file_bytes)),
            "placeholder_email": placeholder,
            "resume_id": str(resume.id),
        },
    )


def resolve_candidate_from_parse(
    *,
    organization,
    parsed: ParseResult,
    file_name: str,
) -> tuple[Candidate, bool]:
    personal = (parsed.data or {}).get("personal_info") or {}
    email = (personal.get("email") or "").strip().lower()
    placeholder = False
    if not email:
        placeholder = True
        email = _placeholder_email(file_name)

    full_name = (personal.get("full_name") or "").strip()
    first_name, last_name = _split_name(full_name)
    candidate, created = Candidate.objects.get_or_create(
        organization=organization,
        email=email,
        defaults={
            "first_name": first_name,
            "last_name": last_name,
            "phone": personal.get("phone") or "",
            "linkedin_url": personal.get("linkedin_url") or "",
            "github_url": personal.get("github_url") or "",
        },
    )
    if not created:
        changed_fields = []
        for field, value in {
            "first_name": first_name,
            "last_name": last_name,
            "phone": personal.get("phone") or "",
            "linkedin_url": personal.get("linkedin_url") or "",
            "github_url": personal.get("github_url") or "",
        }.items():
            if value and not getattr(candidate, field):
                setattr(candidate, field, value)
                changed_fields.append(field)
        if changed_fields:
            candidate.save(update_fields=[*changed_fields, "updated_at"])
    return candidate, placeholder


def persist_uploaded_resume(
    *,
    application: Application,
    file_name: str,
    file_bytes: bytes,
    content_type: str,
    uploaded_by,
) -> Resume:
    file_hash = hashlib.sha256(file_bytes).hexdigest()
    existing = Resume.objects.filter(application=application, file_hash=file_hash).first()
    if existing:
        return existing

    file_ext = file_name.split(".")[-1].lower() if "." in file_name else "bin"
    file_path = f"{application.organization_id}/{application.candidate_id}/{file_hash}.{file_ext}"
    from django.core.files.base import ContentFile

    upload_file("resumes", file_path, ContentFile(file_bytes, name=file_name), content_type)
    return Resume.objects.create(
        candidate=application.candidate,
        application=application,
        file_url=file_path,
        file_name=file_name,
        file_size=len(file_bytes),
        mime_type=content_type,
        file_hash=file_hash,
        raw_text="",
        status=Resume.Status.COMPLETED,
        uploaded_by=uploaded_by if getattr(uploaded_by, "is_authenticated", False) else None,
    )


def persist_parsed_resume(
    *,
    resume: Resume,
    application: Application,
    candidate: Candidate,
    raw_text: str,
    parsed: ParseResult,
) -> ParsedResume:
    resume.raw_text = raw_text
    resume.status = Resume.Status.COMPLETED
    resume.save(update_fields=["raw_text", "status", "updated_at"])
    parsed_resume, _created = ParsedResume.objects.update_or_create(
        resume=resume,
        defaults={
            "candidate": candidate,
            "application": application,
            "status": ParsedResume.Status.COMPLETED,
            "data": parsed.data,
            "confidence": parsed.confidence,
            "parser_model": parsed.model,
            "validation_errors": parsed.validation_errors or [],
            "token_usage": parsed.token_usage or {},
            "estimated_cost": parsed.estimated_cost or 0,
            "parsed_at": timezone.now(),
        },
    )
    return parsed_resume


def process_score_item(item: BatchItem) -> BatchItem:
    application = Application.objects.select_related("candidate", "job", "organization").get(
        id=item.metadata["application_id"],
        organization=item.batch.organization,
    )
    score_application(application, force=True)
    return mark_item_completed(item, application=application, candidate=application.candidate)


def process_pipeline_item(item: BatchItem) -> BatchItem:
    batch = item.batch
    params = batch.params or {}
    action = params.get("action")
    application = Application.objects.select_related("candidate", "job", "organization").get(
        id=item.metadata["application_id"],
        organization=batch.organization,
    )
    note = f"Bulk {action} via batch {batch.id}"

    if action == "move":
        stage_id = params.get("target_stage_id")
        if stage_id:
            stage = PipelineStage.objects.get(id=stage_id, job=application.job, is_active=True)
            move_application_to_stage(application, stage, moved_by=batch.initiated_by, notes=note)
        else:
            status = params.get("target_status")
            if not status:
                raise ValueError("target_status or target_stage_id is required for move action.")
            application.transition_status(status, changed_by=batch.initiated_by, notes=note)
    elif action == "reject":
        application.transition_status(
            Application.Status.REJECTED,
            changed_by=batch.initiated_by,
            notes=note,
        )
    elif action == "archive":
        application.transition_status(
            Application.Status.REJECTED,
            changed_by=batch.initiated_by,
            notes=f"{note}; archived from active pipeline.",
        )
    else:
        raise ValueError("Unsupported pipeline action.")

    application.refresh_from_db()
    return mark_item_completed(item, application=application, candidate=application.candidate)


def _split_name(full_name: str) -> tuple[str, str]:
    parts = full_name.split()
    if not parts:
        return "Unknown", ""
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], " ".join(parts[1:])


def _placeholder_email(file_name: str) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", file_name.lower()).strip("-") or "candidate"
    digest = hashlib.sha1(file_name.encode("utf-8")).hexdigest()[:10]  # noqa: S324
    return f"{base}-{digest}@placeholder.recruitai.local"
