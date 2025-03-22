from django.contrib import admin

# Register your models here.
from .models import Attempt, Answer

admin.site.register(Attempt)
admin.site.register(Answer)