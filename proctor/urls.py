from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.proctor_dashboard, name='proctor_dashboard'),

    # Exam Management
    path('create-exam/', views.create_exam, name='create_exam'),
    path('edit-exam/<uuid:exam_id>/', views.edit_exam, name='edit_exam'),
    path('delete-exam/<uuid:exam_id>/', views.delete_exam, name='delete_exam'),

    # Student Invitation
    path('invite-students/<uuid:exam_id>/', views.invite_students, name='invite_students'),

    # Question Management
    path('exam/<uuid:exam_id>/questions/', views.manage_questions, name='manage_questions'),
    path('question/delete/<uuid:question_id>/', views.delete_question, name='delete_question'),
    path('question/edit/<uuid:question_id>/', views.edit_question, name='edit_question'),
]
