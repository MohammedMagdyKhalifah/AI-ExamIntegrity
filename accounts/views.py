from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.core.mail import EmailMessage
from django.utils import timezone
from django.urls import reverse
from .models import PasswordReset

@login_required
def Home(request):
    return render(request, 'integrity_app/index.html')

def RegisterView(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
            return redirect('register')

        if len(password) < 5:
            messages.error(request, "Password must be at least 5 characters")
            return redirect('register')

        User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            email=email,
            username=username,
            password=password
        )
        messages.success(request, "Account created. Login now")
        return redirect('login')

    return render(request, 'pages/register.html')

def LoginView(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')

        messages.error(request, "Invalid login credentials")
        return redirect('login')

    return render(request, 'pages/login.html')

def LogoutView(request):
    logout(request)
    return redirect('login')

def ForgotPassword(request):
    if request.method == "POST":
        email = request.POST.get('email')

        if not User.objects.filter(email=email).exists():
            messages.success(request, "If an account exists with this email, a password reset link has been sent.")
            return redirect('forgot-password')

        user = User.objects.get(email=email)
        new_password_reset = PasswordReset.objects.create(user=user)
        password_reset_url = reverse('reset-password', kwargs={'reset_id': new_password_reset.reset_id})
        full_password_reset_url = f'{request.scheme}://{request.get_host()}{password_reset_url}'
        email_body = f'Reset your password using the link below:\n\n{full_password_reset_url}'

        email_message = EmailMessage(
            'Reset your password',
            email_body,
            settings.EMAIL_HOST_USER,
            [email]
        )

        email_message.fail_silently = False
        email_message.send()

        return redirect('password-reset-sent')

    return render(request, 'pages/forgot_password.html')

def PasswordResetSent(request):
    return render(request, 'pages/password_reset_sent.html')

def ResetPassword(request, reset_id):
    try:
        password_reset_entry = PasswordReset.objects.get(reset_id=reset_id)
    except PasswordReset.DoesNotExist:
        messages.error(request, 'Invalid reset ID')
        return redirect('forgot-password')

    if request.method == "POST":
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return redirect('reset-password', reset_id=reset_id)

        if len(password) < 5:
            messages.error(request, 'Password must be at least 5 characters long')
            return redirect('reset-password', reset_id=reset_id)

        expiration_time = password_reset_entry.created_when + timezone.timedelta(minutes=10)
        if timezone.now() > expiration_time:
            messages.error(request, 'Reset link has expired')
            password_reset_entry.delete()
            return redirect('forgot-password')

        user = password_reset_entry.user
        user.set_password(password)
        user.save()
        password_reset_entry.delete()

        messages.success(request, 'Password reset. Proceed to login')
        return redirect('login')

    return render(request, 'pages/reset_password.html')

def About(request):
    return render(request, 'pages/about.html')