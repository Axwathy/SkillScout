from django.urls import path

from .consumers import BatchProgressConsumer

websocket_urlpatterns = [
    path("ws/batch/<uuid:batch_id>/", BatchProgressConsumer.as_asgi()),
]
