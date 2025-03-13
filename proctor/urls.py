from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.proctor_dashboard, name='proctor_dashboard'),
    # Add more proctor-specific URL patterns here as needed.

]