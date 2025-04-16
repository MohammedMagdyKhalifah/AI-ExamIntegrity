from django.contrib import admin
from .models import CustomUser, StudentProfile,ProctorProfile, PasswordReset
# Register your models here.

admin.site.register(CustomUser)
admin.site.register(StudentProfile)
admin.site.register(ProctorProfile)
admin.site.register(PasswordReset)
