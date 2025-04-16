from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from django.conf import settings


class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('student', 'Student'),
        ('proctor', 'Proctor'),
        ('admin', 'Admin'),
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='student')

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"


class StudentProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='student_profile')
    student_id = models.CharField(max_length=30, unique=True, blank=True, null=True)
    national_id = models.CharField(max_length=30, unique=True, blank=True, null=True)
    enrollment_year = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"Student Profile: {self.user.username}"


class ProctorProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='proctor_profile')
    proctor_id = models.CharField(max_length=30, unique=True, blank=True, null=True)
    department = models.CharField(max_length=50, blank=True)
    office_location = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Proctor Profile: {self.user.username}"


class PasswordReset(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reset_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_when = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Password reset for {self.user.username} at {self.created_when}"