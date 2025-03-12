
# integrity_app/urls.py

from django.urls import path
from .views import index, process_frame, process_audio

urlpatterns = [
    path('', index, name='index'),
    path('process-frame/', process_frame, name='process_frame'),
    path('process_audio/', process_audio, name='process_audio'),
]