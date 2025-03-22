from django.urls import path
from student.views import student_my_exams

urlpatterns = [
    # Other URL patterns...
    path('my_exams/', student_my_exams, name='student_my_exams'),
]