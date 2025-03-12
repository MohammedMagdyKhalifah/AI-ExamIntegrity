# integrity_app/routing.py
# Using path instead of re_path
# integrity_app/routing.py

# integrity_app/routing.py

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/listen/?$', consumers.TranscriptConsumer.as_asgi()),
]