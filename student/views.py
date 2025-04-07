from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from accounts.decorators import student_required
from proctor.models import Exam, Question
from django.contrib import messages
from .models import Attempt, Answer
from django.http import JsonResponse, HttpResponseBadRequest
import json
from django.views.decorators.http import require_POST





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

@student_required
@login_required
def student_exam_detail(request, exam_id):
    """
    Displays the main information for an exam from the student's perspective.
    Only exams the student is registered for are accessible.
    Shows essential details along with the number of questions.
    """
    # Ensure the student is registered for the exam
    exam = get_object_or_404(Exam, exam_id=exam_id, student_list=request.user)
    # Get the count of related questions
    question_count = exam.questions.count()  # assumes related_name="questions" in Question model
    now = timezone.now()  # This should return a timezone-aware datetime
    context = {
        'exam': exam,
        'question_count': question_count,
        'now': now,
    }
    return render(request, 'student/exam_detail.html', context)


@student_required
@login_required
def start_exam(request, exam_id):
    """
    Checks exam availability and student's attempt count.
    On POST, creates a new Attempt and redirects to the first question.
    """
    now = timezone.now()
    exam = get_object_or_404(Exam, exam_id=exam_id, student_list=request.user)

    # Ensure exam is available: start_time <= now < end_time.
    if not (exam.start_time <= now < exam.end_time):
        messages.error(request, "Exam is not available at this time.")
        return redirect('student_exam_detail', exam_id=exam.exam_id)

    # Check if allowed attempt count is not exceeded.
    attempt_count = exam.attempts.filter(student=request.user).count()
    if attempt_count >= exam.attempt:
        messages.error(request, "You have reached the maximum allowed attempts for this exam.")
        return redirect('student_exam_detail', exam_id=exam.exam_id)

    if request.method == "POST":
        new_attempt = exam.attempts.create(student=request.user, status='in_progress')
        # Redirect to the first question page.
        return redirect('exam_question', attempt_id=new_attempt.attempt_id, question_number=1)

    context = {
        'exam': exam,
        'attempt_count': attempt_count,
        'allowed_attempts': exam.attempt,
        'now': now,
        'duration': exam.duration,
    }
    return render(request, 'student/start_exam.html', context)


@student_required
@login_required
def exam_submit(request, attempt_id):
    """
    Finalizes the exam attempt.
    On POST:
      - Iterates over each Answer in the Attempt.
      - For each answer, calculates its grade by comparing the student's answer
        with the question's correct answer (using trimmed, case-insensitive comparison).
      - Updates each Answer's grade, sums these into a total score,
        marks the attempt as completed, records the end time, and saves the Attempt.
    """
    attempt = get_object_or_404(Attempt, attempt_id=attempt_id, student=request.user)

    if request.method == "POST":
        total_score = 0
        # Loop through all answers associated with this attempt.
        for answer in attempt.answers.all():
            question = answer.question
            # Check if both student's answer and correct answer exist.
            if answer.answer_text and question.correct_answer:
                # Compare after stripping whitespace and converting to lower case.
                if answer.answer_text.strip().lower() == question.correct_answer.strip().lower():
                    # Award full points from the question grade if available, otherwise 0.
                    answer.grade = question.grade if question.grade is not None else 0
                else:
                    answer.grade = 0
            else:
                answer.grade = 0
            answer.save()
            total_score += answer.grade

        attempt.score = total_score
        attempt.status = 'completed'
        attempt.end_time = timezone.now()
        attempt.save()
        messages.success(request, "Exam submitted successfully.")
        # Redirect to a result page or any page you wish (here, redirecting to login as an example).
        return redirect('student_exam_detail',exam_id=attempt.exam_id)

    return render(request, 'student/exam_submit.html', {'attempt': attempt})

@student_required
@login_required
def exam_interface(request, attempt_id):
    """
    Displays the exam interface: lists all questions of the exam for this attempt.
    """
    attempt = get_object_or_404(Attempt, attempt_id=attempt_id, student=request.user)
    exam = attempt.exam
    questions = exam.questions.all()  # Ensure your Question model FK has related_name="questions"
    context = {
        'exam': exam,
        'attempt': attempt,
        'questions': questions,
        'now': timezone.now(),
        'duration': exam.duration,  # Used for the countdown timer
    }
    return render(request, 'student/exam_interface.html', context)


@require_POST
@student_required
@login_required
def submit_answer(request):
    """
    AJAX view to process an individual question answer.
    It:
    - Receives JSON data with 'attempt_id', 'question_id', and 'answer_text'.
    - Retrieves (or creates) the Answer record and calculates its grade immediately.
    - Updates the overall attempt score and saves both the Answer and Attempt.
    - Returns a JSON response with the awarded grade and updated total score.
    """
    try:
        data = json.loads(request.body)
        attempt_id = data.get('attempt_id')
        question_id = data.get('question_id')
        answer_text = data.get('answer_text', '').strip()
    except Exception as e:
        return HttpResponseBadRequest("Invalid JSON data")

    # Retrieve the attempt (ensure it belongs to the logged-in student)
    attempt = get_object_or_404(Attempt, attempt_id=attempt_id, student=request.user)
    # Retrieve the question; assumes the question belongs to the exam for this attempt
    question = get_object_or_404(Question, question_id=question_id, exam=attempt.exam)

    # Get or create an Answer record for this question in the current attempt.
    answer, created = Answer.objects.get_or_create(attempt=attempt, question=question)
    answer.answer_text = answer_text

    # Calculate the grade:
    # For a simple case, if the answer (lowercased) exactly matches the correct_answer (lowercased),
    # award full grade, otherwise award 0.
    if question.correct_answer and answer_text.lower() == question.correct_answer.lower():
        answer.grade = question.grade or 0
    else:
        answer.grade = 0
    answer.save()

    # Update the total score for the attempt (summing all answers' grades)
    total_score = sum(a.grade or 0 for a in attempt.answers.all())
    attempt.score = total_score
    attempt.save()

    return JsonResponse({
        'success': True,
        'grade_awarded': answer.grade,
        'total_score': total_score,
    })


@student_required
@login_required
def exam_question(request, attempt_id, question_number):
    """
    Displays a single question for an exam attempt.
    On POST, saves or updates the student's answer (without showing any grade).
    Navigates to the next question or, if it is the last question, to the exam submission page.
    """
    attempt = get_object_or_404(Attempt, attempt_id=attempt_id, student=request.user)
    exam = attempt.exam
    # Retrieve all questions (assumed ordered by question_id)
    questions = exam.questions.all().order_by('question_id')
    total_questions = questions.count()

    if question_number < 1 or question_number > total_questions:
        messages.error(request, "Invalid question number.")
        return redirect('exam_question', attempt_id=attempt_id, question_number=1)

    current_question = questions[question_number - 1]

    # Retrieve any existing answer for this question
    try:
        answer_obj = Answer.objects.get(attempt=attempt, question=current_question)
    except Answer.DoesNotExist:
        answer_obj = None

    if request.method == "POST":
        answer_text = request.POST.get('answer', '').strip()
        if answer_obj:
            answer_obj.answer_text = answer_text
            answer_obj.save()
        else:
            Answer.objects.create(
                attempt=attempt,
                question=current_question,
                answer_text=answer_text
            )
        # Do not calculate or display the grade now.
        if question_number < total_questions:
            return redirect('exam_question', attempt_id=attempt_id, question_number=question_number + 1)
        else:
            return redirect('exam_submit', attempt_id=attempt_id)

    context = {
        'exam': exam,
        'attempt': attempt,
        'current_question': current_question,
        'question_number': question_number,
        'total_questions': total_questions,
        'existing_answer': answer_obj.answer_text if answer_obj else '',
    }
    return render(request, 'student/exam_question.html', context)