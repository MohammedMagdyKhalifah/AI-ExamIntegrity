from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def student_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Ensure user is authenticated and is a student
        if not request.user.is_authenticated or request.user.user_type != 'student':
            messages.error(request, "You must be a student to access this page.")
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def proctor_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Ensure user is authenticated and is a proctor
        if not request.user.is_authenticated or request.user.user_type != 'proctor':
            messages.error(request, "You must be a proctor to access this page.")
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view