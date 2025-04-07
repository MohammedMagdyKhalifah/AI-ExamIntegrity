from django.urls import path
from student.views import student_my_exams, student_exam_detail, start_exam, exam_submit, exam_interface, submit_answer, exam_question

urlpatterns = [
    # Other URL patterns...
    path('my_exams/', student_my_exams, name='student_my_exams'),
    path('exam_detail/<uuid:exam_id>/', student_exam_detail, name='student_exam_detail'),
    path('start_exam/<uuid:exam_id>/', start_exam, name='start_exam'),
    path('exam/<uuid:attempt_id>/', exam_interface, name='exam_interface'),
    path('exam/submit_answer/', submit_answer, name='submit_answer'),
    path('exam/submit/<uuid:attempt_id>/', exam_submit, name='exam_submit'),
    path('exam/<uuid:attempt_id>/question/<int:question_number>/', exam_question, name='exam_question'),

]
