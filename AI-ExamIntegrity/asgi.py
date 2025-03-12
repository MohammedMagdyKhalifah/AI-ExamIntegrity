"""
ASGI config for AI-ExamIntegrity project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""
# AI-ExamIntegrity/asgi.py

import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
import integrity_app.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AI-ExamIntegrity.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            integrity_app.routing.websocket_urlpatterns
        )
    ),
})