
# integrity_app/urls.py

from django.urls import path

from accounts import views
from .views import index, process_frame, upload_audio

urlpatterns = [
    path('', index, name='student_dashboard'),
    path('process-frame/', process_frame, name='process_frame'),
    path('upload_audio/', upload_audio, name='upload_audio'),

]