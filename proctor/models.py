
# Create your models here.

import uuid
from django.db import models
from django.conf import settings


class Exam(models.Model):
    # Unique exam identifier; using UUID ensures a unique value
    exam_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Optional: A title and description for the exam
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    # When the exam is scheduled to start and end
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    # Duration of the exam; computed automatically if not provided.
    duration = models.DurationField(blank=True, null=True, help_text="Duration of the exam ex: 2:30:00")

    # The proctor who created/oversees this exam
    proctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='exams',
        limit_choices_to={'user_type': 'proctor'}
    )

    # A list of students registered to take this exam; many-to-many relation
    student_list = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='exams_taken',
        limit_choices_to={'user_type': 'student'}
    )

    # An overall grade for the exam (could be computed later)
    grade = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    # Number of allowed attempts (or actual attempt count, as needed)
    attempt = models.PositiveIntegerField(default=1)

    # The current status of the exam; choices can be adjusted as needed
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('paused', 'Paused'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')

    def __str__(self):
        return f"Exam {self.exam_id} - {self.title}"


class Question(models.Model):
    # Unique identifier for each question
    question_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # The text content of the question
    question_text = models.TextField()

    # Link the question to an exam.
    exam = models.ForeignKey('Exam', on_delete=models.CASCADE, related_name='questions')

    # Optional media (image, video, audio) associated with the question
    question_media = models.FileField(upload_to='question_media/', blank=True, null=True)

    # The type of question, chosen from predefined choices
    QUESTION_TYPE_CHOICES = [
        ('MCQ', 'Multiple Choice'),
        ('TF', 'True/False'),
        ('SA', 'Short Answer'),
        # Add more types as needed.
    ]

    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES)

    # For multiple choice questions, store the list of choices as JSON (e.g., a list of strings)
    choiceA =  models.CharField(max_length=255, blank=True, null=True)
    choiceB = models.CharField(max_length=255, blank=True, null=True)
    choiceC = models.CharField(max_length=255, blank=True, null=True)
    choiceD = models.CharField(max_length=255, blank=True, null=True)

    # The correct answer(s), stored in a flexible JSON format. For MCQ, it can be a string or a list.
    correct_answer = models.CharField(max_length=255, blank=True, null=True)

    # The grade (or weight) for this question
    grade = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)

    # A comma separated list of keywords associated with the question
    keywords = models.TextField(
        blank=True,
        help_text="Comma separated list of keywords"
    )

    def __str__(self):
        # Return the first 50 characters of the question text for easy identification
        return f"Question {self.question_id}: {self.question_text[:50]}"