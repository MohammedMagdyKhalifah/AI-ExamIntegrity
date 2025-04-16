
# integrity_app/urls.py

from django.urls import path

from accounts import views
from .views import index, process_frame, process_audio
from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView

urlpatterns = [
    path('', index, name='student_dashboard'),
    path('process-frame/', process_frame, name='process_frame'),
    path('process_audio/', process_audio, name='process_audio'),
]