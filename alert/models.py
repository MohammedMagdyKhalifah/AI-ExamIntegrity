# Create your models here.
import uuid
from django.db import models
from django.conf import settings


class Alert(models.Model):
    ALERT_TYPE_CHOICES = [
        ('face', 'Face Violation'),
        ('sound', 'Sound Violation'),
        ('navigation', 'Navigation Violation'),
        # Add more alert types as needed.
    ]

    ACTION_TAKEN_CHOICES = [
        ('none', 'None'),
        ('warn', 'Warn Student'),
        ('terminate', 'Terminate Exam'),
        ('resume', 'Resume Exam'),
    ]

    alert_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Link to the proctor (only proctor users are allowed)
    proctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='alerts',
        limit_choices_to={'user_type': 'proctor'}
    )

    alert_type = models.CharField(max_length=50, choices=ALERT_TYPE_CHOICES)

    alert_time = models.DateTimeField(auto_now_add=True)

    alert_description = models.TextField(blank=True, help_text="Description of the alert")

    action_taken = models.CharField(
        max_length=20,
        choices=ACTION_TAKEN_CHOICES,
        default='none',
        blank=True,
        help_text="Action taken by the proctor in response to the alert"
    )

    # Link to the attempt that triggered the alert
    attempt = models.ForeignKey(
        'student.Attempt',
        on_delete=models.CASCADE,
        related_name='alerts'
    )

    def __str__(self):
        return f"Alert {self.alert_id} ({self.get_alert_type_display()}) for Attempt {self.attempt.attempt_id}"