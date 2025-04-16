# AI-ExamIntegrity/asgi.py
import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application

import integrity_app
from integrity_app.routing import websocket_urlpatterns  # Adjust this import if needed

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "AI-ExamIntegrity.settings")
django.setup()

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            integrity_app.routing.websocket_urlpatterns
        )
    ),
})