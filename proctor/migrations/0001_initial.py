# Generated by Django 4.2.10 on 2025-03-22 20:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Exam',
            fields=[
                ('exam_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('grade', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('attempt', models.PositiveIntegerField(default=1)),
                ('status', models.CharField(choices=[('scheduled', 'Scheduled'), ('ongoing', 'Ongoing'), ('completed', 'Completed'), ('paused', 'Paused'), ('cancelled', 'Cancelled')], default='scheduled', max_length=20)),
                ('proctor', models.ForeignKey(limit_choices_to={'user_type': 'proctor'}, on_delete=django.db.models.deletion.CASCADE, related_name='exams', to=settings.AUTH_USER_MODEL)),
                ('student_list', models.ManyToManyField(limit_choices_to={'user_type': 'student'}, related_name='exams_taken', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('question_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('question_text', models.TextField()),
                ('question_media', models.FileField(blank=True, null=True, upload_to='question_media/')),
                ('question_type', models.CharField(choices=[('MCQ', 'Multiple Choice'), ('TF', 'True/False'), ('SA', 'Short Answer')], max_length=20)),
                ('choiceA', models.CharField(blank=True, max_length=255, null=True)),
                ('choiceB', models.CharField(blank=True, max_length=255, null=True)),
                ('choiceC', models.CharField(blank=True, max_length=255, null=True)),
                ('choiceD', models.CharField(blank=True, max_length=255, null=True)),
                ('correct_answer', models.CharField(blank=True, max_length=255, null=True)),
                ('grade', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('keywords', models.TextField(blank=True, help_text='Comma separated list of keywords')),
                ('exam', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='proctor.exam')),
            ],
        ),
    ]
