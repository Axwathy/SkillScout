from rest_framework import serializers

from .models import BatchItem, BatchJob, ScheduledBatchOperation


class BatchItemSerializer(serializers.ModelSerializer):
    application_id = serializers.UUIDField(source="application.id", read_only=True)
    candidate_id = serializers.UUIDField(source="candidate.id", read_only=True)

    class Meta:
        model = BatchItem
        fields = (
            "id",
            "label",
            "status",
            "error",
            "application_id",
            "candidate_id",
            "metadata",
            "started_at",
            "completed_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class BatchJobSerializer(serializers.ModelSerializer):
    initiated_by_email = serializers.EmailField(
        source="initiated_by.email",
        read_only=True,
        default=None,
    )

    class Meta:
        model = BatchJob
        fields = (
            "id",
            "job_type",
            "status",
            "total_count",
            "processed_count",
            "failed_count",
            "params",
            "result",
            "initiated_by_email",
            "created_at",
            "started_at",
            "completed_at",
        )
        read_only_fields = fields


class BatchProgressSerializer(BatchJobSerializer):
    items = BatchItemSerializer(many=True, read_only=True)

    class Meta(BatchJobSerializer.Meta):
        fields = BatchJobSerializer.Meta.fields + ("items",)


class ScheduledBatchOperationSerializer(serializers.ModelSerializer):
    created_by_email = serializers.EmailField(
        source="created_by.email",
        read_only=True,
        default=None,
    )
    last_batch_id = serializers.UUIDField(source="last_batch.id", read_only=True, default=None)

    class Meta:
        model = ScheduledBatchOperation
        fields = (
            "id",
            "job_type",
            "params",
            "frequency",
            "is_active",
            "next_run_at",
            "last_run_at",
            "last_batch_id",
            "created_by_email",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "is_active",
            "last_run_at",
            "last_batch_id",
            "created_by_email",
            "created_at",
            "updated_at",
        )
