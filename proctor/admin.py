from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Exam, Question

admin.site.register(Exam)
admin.site.register(Question)

