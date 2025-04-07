import django
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from integrity_app.consumers import face_monitor_ws

application = ProtocolTypeRouter({
    # Django's ASGI application to handle traditional HTTP requests.
    "http":  django.core.asgi.get_asgi_application(),
    # WebSocket chat handler.
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path("ws/monitor/", face_monitor_ws.as_asgi()),
        ])
    ),
})