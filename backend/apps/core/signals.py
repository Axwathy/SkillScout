from __future__ import annotations

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from apps.analytics.models import DailyAnalyticsSnapshot
from apps.candidates.models import Application, ApplicationHistory, Candidate, ParsedResume, Resume
from apps.core.cache import invalidate_org_cache
from apps.jobs.models import Job
from apps.pipeline.models import PipelineStage, PipelineStageHistory


@receiver([post_save, post_delete], sender=Job)
def invalidate_job_org_cache(sender, instance: Job, **kwargs):
    invalidate_org_cache(instance.organization_id)


@receiver([post_save, post_delete], sender=Candidate)
def invalidate_candidate_org_cache(sender, instance: Candidate, **kwargs):
    invalidate_org_cache(instance.organization_id)


@receiver([post_save, post_delete], sender=Application)
def invalidate_application_org_cache(sender, instance: Application, **kwargs):
    invalidate_org_cache(instance.organization_id)


@receiver([post_save, post_delete], sender=ApplicationHistory)
def invalidate_application_history_org_cache(sender, instance: ApplicationHistory, **kwargs):
    organization_id = (
        Application.objects.filter(id=instance.application_id)
        .values_list("organization_id", flat=True)
        .first()
    )
    invalidate_org_cache(organization_id)


@receiver([post_save, post_delete], sender=Resume)
def invalidate_resume_org_cache(sender, instance: Resume, **kwargs):
    organization_id = (
        Candidate.objects.filter(id=instance.candidate_id)
        .values_list("organization_id", flat=True)
        .first()
    )
    invalidate_org_cache(organization_id)


@receiver([post_save, post_delete], sender=ParsedResume)
def invalidate_parsed_resume_org_cache(sender, instance: ParsedResume, **kwargs):
    organization_id = (
        Candidate.objects.filter(id=instance.candidate_id)
        .values_list("organization_id", flat=True)
        .first()
    )
    invalidate_org_cache(organization_id)


@receiver([post_save, post_delete], sender=PipelineStage)
def invalidate_pipeline_stage_org_cache(sender, instance: PipelineStage, **kwargs):
    organization_id = (
        Job.objects.filter(id=instance.job_id).values_list("organization_id", flat=True).first()
    )
    invalidate_org_cache(organization_id)


@receiver([post_save, post_delete], sender=PipelineStageHistory)
def invalidate_pipeline_history_org_cache(sender, instance: PipelineStageHistory, **kwargs):
    organization_id = (
        Application.objects.filter(id=instance.application_id)
        .values_list("organization_id", flat=True)
        .first()
    )
    invalidate_org_cache(organization_id)


@receiver([post_save, post_delete], sender=DailyAnalyticsSnapshot)
def invalidate_analytics_snapshot_org_cache(sender, instance: DailyAnalyticsSnapshot, **kwargs):
    invalidate_org_cache(instance.organization_id)
