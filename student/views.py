from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from accounts.decorators import student_required
from proctor.models import Exam

@student_required
@login_required
def student_my_exams(request):
    """
    Displays the list of exams available to the logged-in student,
    divided into ongoing (available to take now) and upcoming exams.
    Ongoing: start_time <= now and end_time > now.
    Upcoming: start_time > now.
    """
    now = timezone.now()
    ongoing_exams = Exam.objects.filter(
        student_list=request.user,
        start_time__lte=now,
        end_time__gt=now
    )
    upcoming_exams = Exam.objects.filter(
        student_list=request.user,
        start_time__gt=now
    )
    context = {
        'ongoing_exams': ongoing_exams,
        'upcoming_exams': upcoming_exams
    }
    return render(request, 'student/my_exams.html', context)