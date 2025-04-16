
# Create your models here.
import uuid
from django.db import models
from django.conf import settings


class Attempt(models.Model):
    # Unique identifier for each attempt
    attempt_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Link to the exam that this attempt is for
    exam = models.ForeignKey('proctor.Exam', on_delete=models.CASCADE, related_name='attempts')

    # Link to the student making the attempt (only students allowed)
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='attempts',
        limit_choices_to={'user_type': 'student'}
    )

    # The current status of the attempt
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('paused', 'Paused'),
        ('terminated', 'Terminated'),
    ]

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')

    # When the attempt started
    start_time = models.DateTimeField(auto_now_add=True)

    # When the attempt ended; can be null if still in progress
    end_time = models.DateTimeField(blank=True, null=True)

    # Number of times a violation was detected during this attempt
    violation_count = models.PositiveIntegerField(default=0)

    # Overall score for the attempt (if applicable)
    score = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"Attempt {self.attempt_id} for {self.exam.title} by {self.student.username}"


class Answer(models.Model):
    # Unique identifier for each answer
    answer_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Link to the attempt this answer belongs to
    attempt = models.ForeignKey(Attempt, on_delete=models.CASCADE, related_name='answers')

    # Link to the corresponding question (assumes the Question model is in the exams app)
    question = models.ForeignKey('proctor.Question', on_delete=models.CASCADE, related_name='answers')

    # The answer provided by the student
    answer_text = models.TextField()

    # When the answer was submitted
    date_submitted = models.DateTimeField(auto_now_add=True)

    # Grade (or points awarded) for this answer
    grade = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    # Flag to indicate if this answer has a violation (e.g. suspected cheating)
    violation_flag = models.BooleanField(default=False)

    # A URL linking to evidence of the violation, if applicable
    violation_evidence_link = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"Answer {self.answer_id} for Question {self.question.question_id}"