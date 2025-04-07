import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AI-ExamIntegrity.settings')
django_asgi_app = get_asgi_application()

# Import the Channels routing application
from .routing import application as channels_application

# Set the ASGI application to the Channels routing.
application = channels_application