from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from .models import BatchJob
from .serializers import BatchProgressSerializer


class BatchProgressConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.batch_id = self.scope["url_route"]["kwargs"]["batch_id"]
        self.group_name = f"batch_{self.batch_id}"
        user = self.scope.get("user")
        if not user or not user.is_authenticated:
            await self.close(code=4401)
            return
        if not await self._can_access_batch(user, self.batch_id):
            await self.close(code=4403)
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        payload = await self._progress_payload(self.batch_id)
        await self.send_json({"type": "batch.progress", "payload": payload})

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def batch_progress(self, event):
        await self.send_json({"type": "batch.progress", "payload": event["payload"]})

    @database_sync_to_async
    def _can_access_batch(self, user, batch_id) -> bool:
        organization = getattr(getattr(user, "recruiter_profile", None), "organization", None)
        if organization is None:
            return False
        return BatchJob.objects.filter(id=batch_id, organization=organization).exists()

    @database_sync_to_async
    def _progress_payload(self, batch_id):
        batch = (
            BatchJob.objects.select_related("initiated_by")
            .prefetch_related("items")
            .get(id=batch_id)
        )
        return BatchProgressSerializer(batch).data
