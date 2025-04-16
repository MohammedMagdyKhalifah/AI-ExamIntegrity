from django.urls import re_path
from .consumers import AudioConsumer

websocket_urlpatterns = [
    re_path(r'^ws/process_audio/$', AudioConsumer.as_asgi(), name='process_audio'),
]