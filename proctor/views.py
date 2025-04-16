from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages
from .models import Exam, Question
from .forms import ExamForm, QuestionForm
from django.contrib.auth import get_user_model
from accounts.decorators import proctor_required
import uuid 

@proctor_required
@login_required
def proctor_dashboard(request):
    exams = Exam.objects.filter(proctor=request.user)
    return render(request, 'proctor/dashboard.html', {'exams': exams})

@proctor_required
@login_required
def create_exam(request):
    if request.method == 'POST':
        form = ExamForm(request.POST)
        if form.is_valid():
            exam = form.save(commit=False)
            exam.proctor = request.user
            exam.exam_id = uuid.uuid4()  # Force a new unique ID, no edit!
            exam.save()
            return redirect('proctor_dashboard')
    else:
        # ⛔ Start from scratch – no instance at all
        form = ExamForm()

    return render(request, 'proctor/create_exam.html', {
        'form': form,
    })
@proctor_required
@login_required
def edit_exam(request, exam_id):
    exam = get_object_or_404(Exam, exam_id=exam_id)
    
    if request.method == 'POST':
        form = ExamForm(request.POST, instance=exam)
        if form.is_valid():
            form.save()
            return redirect('proctor_dashboard')
    else:
        form = ExamForm(instance=exam)

    return render(request, 'proctor/create_exam.html', {
        'form': form,
    })

@proctor_required
@login_required
def delete_exam(request, exam_id):
    exam = get_object_or_404(Exam, exam_id=exam_id, proctor=request.user)
    exam.delete()
    return redirect('proctor_dashboard')

@proctor_required
@login_required
def invite_students(request, exam_id):
    exam = get_object_or_404(Exam, exam_id=exam_id, proctor=request.user)
    User = get_user_model()
    students = User.objects.filter(user_type='student')

    if request.method == 'POST':
        action = request.POST.get('action')
        student_id = request.POST.get('student_id')

        try:
            student = User.objects.get(id=student_id, user_type='student')
        except User.DoesNotExist:
            messages.error(request, "Student ID not found.")
            return redirect('invite_students', exam_id=exam.exam_id)

        if action == 'add':
            exam.student_list.add(student)
            messages.success(request, f"Student {student.username} added.")
        elif action == 'remove':
            exam.student_list.remove(student)
            messages.warning(request, f"Student {student.username} removed.")
        return redirect('invite_students', exam_id=exam.exam_id)

    invited = exam.student_list.all()
    return render(request, 'proctor/invite_students.html', {
        'exam': exam,
        'students': students,
        'invited': invited
    })

@proctor_required
@login_required
def manage_questions(request, exam_id):
    exam = get_object_or_404(Exam, exam_id=exam_id, proctor=request.user)
    questions = exam.questions.all().order_by('question_id')

    if request.method == 'POST':
        form = QuestionForm(request.POST, request.FILES)
        if form.is_valid():
            question = form.save(commit=False)
            question.exam = exam
            question.save()
            return redirect('manage_questions', exam_id=exam.exam_id)
    else:
        form = QuestionForm()

    return render(request, 'proctor/manage_questions.html', {
        'exam': exam,
        'questions': questions,
        'form': form,
    })

@proctor_required
@login_required
def delete_question(request, question_id):
    question = get_object_or_404(Question, question_id=question_id)
    exam_id = question.exam.exam_id
    if request.user != question.exam.proctor:
        return HttpResponseForbidden("You are not allowed to delete this question.")
    question.delete()
    return redirect('manage_questions', exam_id=exam_id)

@proctor_required
@login_required
def edit_question(request, question_id):
    question = get_object_or_404(Question, question_id=question_id)
    exam = question.exam

    if request.user != exam.proctor:
        return HttpResponseForbidden("You are not allowed to edit this question.")

    if request.method == 'POST':
        form = QuestionForm(request.POST, request.FILES, instance=question)
        if form.is_valid():
            form.save()
            return redirect('manage_questions', exam_id=exam.exam_id)
    else:
        form = QuestionForm(instance=question)

    return render(request, 'proctor/edit_question.html', {
        'form': form,
        'question': question,
        'exam': exam,
    })
